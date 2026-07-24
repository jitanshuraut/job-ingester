from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class HarnessScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://boards-api.greenhouse.io/v1/boards/harnessinc/jobs?content=true"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            return {}

    def is_india(self, item) -> bool:
        def _has_india(name: str) -> bool:
            lower = name.lower()
            if "india" not in lower:
                return False
            if "indiana" in lower or "indianapolis" in lower:
                return False
            return True

        loc = item.get("location") or {}
        if _has_india(loc.get("name", "")):
            return True
        for office in item.get("offices", []):
            if _has_india(office.get("name", "")):
                return True
        return False

    def parse(self, data) -> list[Job]:
        items = data.get("jobs", [])
        job_list = []
        for item in items:
            if not self.is_india(item):
                continue
            loc = item.get("location") or {}
            offices = item.get("offices", [])
            location = loc.get("name", "")
            if not location and offices:
                location = offices[0].get("name", "")
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id", "")),
                company="Harness",
                location=location,
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("first_published", "")),
            )
            job_list.append(job)
        return job_list
