from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import json


class UberScraper(BaseScraper):
    API_URL = "https://www.uber.com/api/loadSearchJobsResults?localeCode=en"
    PAGE_SIZE = 100
    ENGINEER_KEYWORDS = ["engineer", "software", "developer", "backend", "frontend",
                         "fullstack", "infrastructure", "platform", "data", "android", "ios"]

    def _fetch_page(self, page: int) -> list[dict]:
        payload = {
            "limit": self.PAGE_SIZE,
            "page": page,
            "params": {
                "location": [{"country": "IND"}],
            },
            "sort": {"order": "DESC", "field": "createdDate"},
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": "https://www.uber.com/us/en/careers/",
            "x-csrf-token": "x",
        }
        try:
            r = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            return (r.json().get("data") or {}).get("results") or []
        except Exception:
            return []

    def fetch_jobs(self) -> list[Job]:
        all_items = []
        page = 0
        while True:
            items = self._fetch_page(page)
            if not items:
                break
            all_items.extend(items)
            if len(items) < self.PAGE_SIZE:
                break
            page += 1

        jobs = []
        for item in all_items:
            title = item.get("title", "")
            dept = (item.get("department") or "").lower()
            team = (item.get("team") or "").lower()
            if not any(kw in dept or kw in team or kw in title.lower()
                       for kw in self.ENGINEER_KEYWORDS):
                continue
            loc = item.get("location") or {}
            city = loc.get("city") or ""
            country_name = loc.get("countryName") or ""
            location = f"{city}, {country_name}".strip(", ")
            job_id = str(item.get("id", ""))
            url = f"https://www.uber.com/global/en/careers/list/{job_id}/"
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Uber",
                location=location,
                url=url,
                posted_date=convert_to_common_format(item.get("updatedDate", "")),
            ))
        return jobs
