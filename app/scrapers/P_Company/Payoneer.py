from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class PayoneerScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://teamme.link/api/projects/0287133b-6912-4eaa-a24a-ba75fef68589/positions"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Origin": "https://careers.payoneer.com",
            "Referer": "https://careers.payoneer.com/",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def parse(self, data) -> list[Job]:
        items = data.get("data", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            return []
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("requisitionId", str(item.get("id", ""))),
                company="Payoneer",
                location=item.get("location", ""),
                url=item.get("applyUrl", ""),
                posted_date=convert_to_common_format(item.get("lastModified", "")),
            )
            job_list.append(job)
        return job_list
