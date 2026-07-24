from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class PhonePeScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://boards-api.greenhouse.io/v1/boards/phonepe/departments"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.phonepe.com',
            'Referer': 'https://www.phonepe.com/',
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        departments = data.get("departments", [])
        job_list = []
        for dept in departments:
            name = (dept.get("name") or "").lower()
            if "engineering" in name or "tech" in name:
                for item in dept.get("jobs", []):
                    loc = item.get("location") or {}
                    job = Job(
                        title=item.get("title", ""),
                        jobid=str(item.get("id", "")),
                        company="PhonePe",
                        location=loc.get("name", ""),
                        url=item.get("absolute_url", ""),
                        posted_date=convert_to_common_format(item.get("updated_at", "")),
                    )
                    job_list.append(job)
        return job_list
