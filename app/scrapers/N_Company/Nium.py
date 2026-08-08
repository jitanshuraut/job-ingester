from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://api.lever.co/v0/postings/nium"


class NiumScraper(BaseScraper):
    def fetch_raw(self):
        resp = requests.get(API_URL, params={}, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36"}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            cats = j.get("categories", {})
            all_locs = cats.get("allLocations", [])
            location = ", ".join(all_locs) if all_locs else cats.get("location", "")
            ts = int(j.get("createdAt", 0) or 0) / 1000
            jobs.append(Job(
                title=j.get("text", ""),
                jobid=str(j.get("id", "")),
                company="Nium",
                location=location,
                url=j.get("hostedUrl", ""),
                posted_date=convert_to_common_format(ts) or "",
            ))
        return jobs