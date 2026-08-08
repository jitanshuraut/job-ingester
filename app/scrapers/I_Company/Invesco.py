from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://invesco.wd1.myworkdayjobs.com/wday/cxs/invesco/IVZ/jobs"


class InvescoScraper(BaseScraper):
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36"})

    def fetch_raw(self):
        all_jobs = []
        total, page = 0, 0
        while True:
            resp = self._session.post(
                API_URL,
                json={"limit": 20, "offset": page * 20, "searchText": ""},
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("jobPostings", [])
            if page == 0:
                total = data.get("total", 0)
            all_jobs.extend(jobs)
            page += 1
            if len(all_jobs) >= total:
                break
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for item in raw:
            if "hyderabad" not in item.get("locationsText", "").lower():
                continue
            ext = item.get("externalPath", "")
            jobs.append(Job(
                title=item.get("title", ""),
                jobid=item["bulletFields"][0] if item.get("bulletFields") else "",
                company="Invesco",
                location=item.get("locationsText", ""),
                url=f"https://invesco.wd1.myworkdayjobs.com/en-US/IVZ{ext}" if ext else "",
                posted_date=convert_to_common_format(item.get("postedOn", "")) or "",
            ))
        return jobs