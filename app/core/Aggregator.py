import inspect
import importlib
import pkgutil
import os
from typing import List, Type
from app.models.job import Job
from app.db.db_client import SupabaseDB
from app.scrapers.base import BaseScraper
from time import sleep
from dataclasses import asdict


class JobAggregator:
    def __init__(self):
        self.db = SupabaseDB().get_client()

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
                        if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj is not BaseScraper:
                            scrapers.append(obj())
                except Exception as e:
                    print(f"❌ Error loading {full_module_path}: {e}")

        return scrapers

    def run(self):
        all_jobs: list[Job] = []
        for scraper in self.discover_scrapers():
            try:
                jobs = scraper.fetch_jobs()
                print(f"✅ {scraper.__class__.__name__} fetched {len(jobs)} jobs.")
                all_jobs.extend(jobs)
                sleep(3)
            except Exception as e:
                print(f"❌ {scraper.__class__.__name__} failed: {e}")

        print(f"🌐 Total jobs collected: {len(all_jobs)}")
        valid_jobs = self._validate_jobs(all_jobs)
        new_jobs: list[Job]=self._push_to_db(valid_jobs)
        return new_jobs


    def _validate_jobs(self, jobs: List[Job]) -> List[Job]:
        seen = set()
        filtered = []

        for job in jobs:
            if not job.url or job.url in seen:
                continue
            seen.add(job.url)
            filtered.append(job)

        print(f"✅ {len(filtered)} jobs after validation.")
        return filtered

    def _push_to_db(self, jobs: list[Job]):
        new_jobs: list[Job] = []
        for job in jobs:
            try:
                self.db.table("jobs").insert(asdict(job)).execute()
                print(f"⬆️  Inserted: {job.title} @ {job.company}")
                new_jobs.append(job) 
            except Exception as e:
                print(f"❌ Failed to insert {job.title} @ {job.company}: {e}")
        return new_jobs
                


