from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API_URL = "https://boards-api.greenhouse.io/v1/boards/imc/jobs"


class IMCScraper(BaseScraper):
    def fetch_raw(self):
        all_jobs = []
        total, page = 0, 1
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36"}
        while True:
            resp = requests.get(API_URL, params={"content": "true", "page": page}, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("jobs", [])
            total = data.get("meta", {}).get("total", len(jobs))
            all_jobs.extend(jobs)
            page += 1
            if len(all_jobs) >= total:
                break
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            loc = j.get("location", {}).get("name", "") if j.get("location") else ""
            jobs.append(Job(
                title=j.get("title", ""),
                jobid=str(j.get("id", "")),
                company="IMC",
                location=loc,
                url=j.get("absolute_url", ""),
                posted_date=convert_to_common_format(j.get("updated_at", "")) or "",
            ))
        return jobs