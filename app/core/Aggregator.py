import inspect
import importlib
import os
import hashlib
import json
from typing import List, Optional, Callable
from app.models.job import Job
from app.db.db_client import SupabaseDB
from app.db import local_db
from app.scrapers.base import BaseScraper
from app.utils.proxy_manager import has_proxies, next_proxy, random_wait, proxy_count
from app.analyzer.fetcher import fetch_description_text
from app.analyzer.extractor import analyze_job_description
from time import sleep
from dataclasses import asdict
from datetime import datetime, timezone


class JobAggregator:
    def __init__(self, log_fn: Optional[Callable[[str], None]] = None):
        self.log = log_fn or print
        local_db.init_db()
        local_db.init_scrape_runs()
        self.db = None
        self.use_supabase = os.getenv("USE_SUPABASE", "true").lower() in ("1", "true", "yes")
        if self.use_supabase:
            try:
                self.db = SupabaseDB().get_client()
            except Exception as e:
                self.log(f"❌ Supabase unavailable, running in local-only mode: {e}")
        else:
            self.log("Supabase disabled via USE_SUPABASE=false, running local-only")
        self._use_proxy = has_proxies()
        if self._use_proxy:
            self.log(f"Proxy rotation enabled ({proxy_count()} proxies)")
        self.analyze_jobs = os.getenv("ANALYZE_JOBS", "false").lower() in ("1", "true", "yes")

    def discover_scrapers(self) -> List[BaseScraper]:
        SCRAPER_ROOT_MODULE = "app.scrapers"
        SCRAPER_ROOT_PATH = "app/scrapers"
        scrapers = []

        for folder in os.listdir(SCRAPER_ROOT_PATH):
            folder_path = os.path.join(SCRAPER_ROOT_PATH, folder)
            if not os.path.isdir(folder_path) or folder.startswith("__"):
                continue

            module_prefix = f"{SCRAPER_ROOT_MODULE}.{folder}"
            for filename in os.listdir(folder_path):
                if not filename.endswith(".py") or filename.startswith("__"):
                    continue

                module_name = filename[:-3]
                full_module_path = f"{module_prefix}.{module_name}"

                try:
                    module = importlib.import_module(full_module_path)
                    for _, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, BaseScraper)
                            and obj is not BaseScraper
                            and obj.__name__ != "PlaywrightScraper"
                        ):
                            scraper = obj()
                            if self._use_proxy:
                                scraper.proxy = next_proxy()
                            scrapers.append(scraper)
                except Exception as e:
                    self.log(f"Error loading {full_module_path}: {e}")

        return scrapers

    def run(self):
        started_at = datetime.now(timezone.utc).isoformat()
        run_id = local_db.create_run(started_at)
        self.log(f"Run #{run_id} started at {started_at}")

        all_jobs: list[Job] = []
        new_jobs: list[Job] = []
        skipped_jobs: list[Job] = []
        scrapers = self.discover_scrapers()
        self.log(f"Discovered {len(scrapers)} scrapers")
        if self.db:
            self._sync_supabase_cache()
        else:
            self.log("Skipping Supabase cache sync (local-only mode)")

        count = 0
        for scraper in scrapers:
            count += 1
            name = scraper.__class__.__name__
            try:
                proxy_label = f" [proxy: {scraper.proxy}]" if scraper.proxy else ""
                self.log(f"[{count}/{len(scrapers)}] Fetching from {name}...{proxy_label}")
                jobs = scraper.fetch_jobs()
                self.log(f"{name} fetched {len(jobs)} jobs.")
                jobs = self._validate_jobs(jobs)
                self._push_new_jobs(jobs, new_jobs, skipped_jobs, scraper.proxy)
                all_jobs.extend(jobs)
                if count < len(scrapers):
                    w = random_wait()
                    self.log(f"Waiting {w:.1f}s before next scraper...")
                    sleep(w)
            except Exception as e:
                self.log(f"{name} failed: {e}")
                if count < len(scrapers):
                    w = random_wait()
                    sleep(w)

        ended_at = datetime.now(timezone.utc).isoformat()
        local_db.complete_run(run_id, len(all_jobs), len(new_jobs), len(skipped_jobs), ended_at)

        if new_jobs:
            local_db.add_run_jobs(run_id, new_jobs, was_new=True)
        if skipped_jobs:
            local_db.add_run_jobs(run_id, skipped_jobs, was_new=False)

        self.log(f"{len(new_jobs)} new jobs inserted to DB.")
        return new_jobs

    def _sync_supabase_cache(self):
        self.log("Syncing local cache from Supabase...")
        cached = local_db.sync_from_supabase(self.db)
        self.log(f"Local cache has {cached} existing jobs")

    def _validate_jobs(self, jobs: List[Job]) -> List[Job]:
        seen = set()
        filtered = []
        for job in jobs:
            if not job.url or job.url in seen:
                continue
            seen.add(job.url)
            filtered.append(job)
        return filtered

    def _push_new_jobs(self, jobs: list[Job], new_jobs: list[Job], skipped_jobs: list[Job], proxy: str | None = None):
        for job in jobs:
            if not job.jobid:
                raw = f"{job.company}|{job.title}|{job.location}"
                job.jobid = hashlib.md5(raw.encode()).hexdigest()[:16]

            if local_db.job_exists(job):
                skipped_jobs.append(job)
                continue

            if self.analyze_jobs:
                analysis = self._analyze_job(job, proxy)
                if analysis:
                    job.experience_years = json.dumps(analysis["experience_years"])
                    job.skills = json.dumps(analysis["skills"])

            try:
                if self.db:
                    self.db.table("jobs").insert(asdict(job)).execute()
                local_db.insert_job(
                    job.title, job.jobid, job.company, job.location,
                    job.url, job.posted_date,
                    experience_years=job.experience_years,
                    skills=job.skills,
                )
                self.log(f"Inserted: {job.title} @ {job.company}")
                new_jobs.append(job)
            except Exception as e:
                self.log(f"Failed to insert {job.title} @ {job.company}: {e}")

    def _analyze_job(self, job: Job, proxy: str | None = None) -> dict | None:
        try:
            self.log(f"Analyzing: {job.title} @ {job.company}...")
            desc = fetch_description_text(job.url, proxy=proxy)
            if not desc:
                self.log(f"No description for {job.title} @ {job.company}")
                return None
            analysis = analyze_job_description(desc)
            self.log(f"Analyzed: {job.title} @ {job.company} ({len(analysis['skills'])} skills)")
            return analysis
        except Exception as e:
            self.log(f"Analysis failed for {job.title} @ {job.company}: {e}")
            return None
