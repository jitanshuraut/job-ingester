from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class YugabyteScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://boards-api.greenhouse.io/v1/boards/yugabyte/jobs"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def parse(self, data) -> list[Job]:
        jobs_data = data.get("jobs", []) if isinstance(data, dict) else []
        if not isinstance(jobs_data, list):
            return []
        job_list = []
        for item in jobs_data:
            location = item.get("location", {}).get("name", "")
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id", "")),
                company="Yugabyte",
                location=location,
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("updated_at", "")),
            )
            job_list.append(job)
        return job_list
