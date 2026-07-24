from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json


class GravitonScraper(BaseScraper):
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def fetch_raw(self):
        try:
            response = self._session.get(
                "https://www.gravitontrading.com/data/greenhouse_jobs.json",
                timeout=30,
            )
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data: dict) -> list[Job]:
        jobs_data = data.get("jobs", [])
        job_list = []
        for item in jobs_data:
            location = item.get("location_text", "")
            if "india" not in location.lower():
                continue
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("gh_jid", "")),
                company="Graviton",
                location=location,
                url=item.get("url", ""),
                posted_date=item.get("details").get("fetched_at"),
            )
            job_list.append(job)
        return job_list
