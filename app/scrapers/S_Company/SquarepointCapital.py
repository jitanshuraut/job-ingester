from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class SquarepointCapitalScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://boards-api.greenhouse.io/v1/boards/squarepointcapital/jobs?content=true"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            return {}

    def parse(self, data) -> list[Job]:
        items = data.get("jobs", [])
        job_list = []
        for item in items:
            loc = item.get("location") or {}
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id", "")),
                company="Squarepoint Capital",
                location=loc.get("name", ""),
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("first_published", "")),
            )
            job_list.append(job)
        return job_list
