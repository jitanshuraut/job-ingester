from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://www.harvey.ai/api/ashby/jobs"


class HarveyScraper(BaseScraper):
    def fetch_raw(self):
        headers = {
            "accept": "*/*",
            "referer": "https://www.harvey.ai/careers",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36",
        }
        resp = requests.get(API_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("jobs", [])

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            sec_locs = [l.get("location", "") if isinstance(l, dict) else str(l) for l in j.get("secondaryLocations", [])]
            location = ", ".join(sec_locs) if sec_locs else j.get("location", "")
            jobs.append(Job(
                title=j.get("title", ""),
                jobid=str(j.get("id", "")),
                company="Harvey",
                location=location,
                url=j.get("jobUrl", "") or "",
                posted_date=convert_to_common_format(j.get("publishedAt", "")) or "",
            ))
        return jobs