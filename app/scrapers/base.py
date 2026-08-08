# app/scrapers/base.py
import json
from typing import List, Optional
from app.models.job import Job
from app.analyzer.fetcher import fetch_description_text
from app.analyzer.extractor import analyze_job_description
from app.utils.proxy_manager import next_proxy, has_proxies

class BaseScraper:
    proxy: Optional[str] = None

    def fetch_jobs(self) -> List[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def fetch_raw(self):
        raise NotImplementedError("Subclasses must implement API call")

    def parse(self, raw_data) -> List[Job]:
        raise NotImplementedError("Subclasses must parse raw data to Job list")

    def enrich_jobs(self, jobs: List[Job]) -> List[Job]:
        proxy = self.proxy
        consecutive_failures = 0
        for job in jobs:
            if not job.url:
                continue
            if job.experience_years or job.skills:
                continue
            try:
                if consecutive_failures >= 2:
                    proxy = None
                description = fetch_description_text(job.url, proxy=proxy)
                if not description and proxy and has_proxies():
                    proxy = next_proxy()
                    consecutive_failures += 1
                    description = fetch_description_text(job.url, proxy=proxy)
                analysis = analyze_job_description(description)
                job.experience_years = json.dumps(analysis["experience_years"])
                job.skills = json.dumps(analysis["skills"])
                if description:
                    consecutive_failures = 0
            except Exception:
                consecutive_failures += 1
                continue
        return jobs
