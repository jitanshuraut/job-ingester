from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://api.smartrecruiters.com/v1/companies/TheNielsenCompany/postings"


class NielsenScraper(BaseScraper):
    SEARCH = "software"

    def fetch_raw(self):
        all_jobs = []
        total, page = 0, 0
        headers = {
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36",
        }
        while True:
            params = {"limit": 50, "offset": page * 50, "search": self.SEARCH}
            resp = requests.get(API_URL, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("content", [])
            total = data.get("totalFound", 0)
            all_jobs.extend(jobs)
            page += 1
            if len(all_jobs) >= total:
                break
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            loc = j.get("location", {})
            full_loc = loc.get("fullLocation", "") if loc else ""
            jobs.append(Job(
                title=j.get("name", ""),
                jobid=str(j.get("id", "")),
                company="Nielsen",
                location=full_loc,
                url=j.get("url", ""),
                posted_date=convert_to_common_format(j.get("releasedDate", "")) or "",
            ))
        return jobs