from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://careers.lamresearch.com/api/pcsx/search"


class LamResearchScraper(BaseScraper):
    LOCATION = "India"

    def fetch_raw(self):
        all_jobs = []
        start, rows, total = 0, 10, 0
        headers = {
            "accept": "application/json, text/plain, */*",
            "referer": "https://careers.lamresearch.com/careers",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36",
        }
        while True:
            params = {
                "domain": "lamresearch.com",
                "query": "",
                "location": self.LOCATION,
                "start": start,
                "rows": rows,
                "sort_by": "timestamp",
                "filter_include_remote": "1",
            }
            resp = requests.get(API_URL, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            positions = data.get("data", {}).get("positions", [])
            if start == 0:
                total = data.get("data", {}).get("count", 0)
            all_jobs.extend(positions)
            start += rows
            if len(all_jobs) >= total:
                break
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for p in raw:
            cannon = p.get("canonicalUrl", "")
            jobs.append(Job(
                title=p.get("name", ""),
                jobid=str(p.get("id", "")),
                company="Lam Research",
                location=", ".join(p.get("standardizedLocations", p.get("locations", []))),
                url=cannon if cannon.startswith("http") else f"https://careers.lamresearch.com{cannon}",
                posted_date=convert_to_common_format(p.get("postedTs", 0)) or "",
            ))
        return jobs