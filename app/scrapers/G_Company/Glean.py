from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API = "https://boards-api.greenhouse.io/v1/boards/gleanwork/jobs"

OFFICES = {
    "bangalore": 4002667005,
    "mountain view": 4002668005,
    "us (remote)": 4002671005,
    "san francisco": 4054115005,
    "new york": 4036909005,
    "nashville": 4050004005,
    "emea (remote)": 4016803005,
    "japan (remote)": 4048192005,
    "london": 4058946005,
}

DEPARTMENTS = {
    "sales": 4006711005,
    "engineering": 4006710005,
    "product": 4007727005,
    "customer outcomes": 4137641005,
    "marketing": 4007726005,
    "support": 4009462005,
    "forward deployment": 4147066005,
    "g&a": 4007725005,
    "design": 4007724005,
    "qa": 4007728005,
}


class GleanScraper(BaseScraper):
    OFFICE_ID = OFFICES["bangalore"]
    DEPARTMENT_ID = DEPARTMENTS["engineering"]

    def fetch_raw(self):
        resp = requests.get(API, params={"content": "true"}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("jobs", [])

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            office_ids = [o["id"] for o in j.get("offices", [])]
            dept_ids = [d["id"] for d in j.get("departments", [])]
            if self.OFFICE_ID and self.OFFICE_ID not in office_ids:
                continue
            if self.DEPARTMENT_ID and self.DEPARTMENT_ID not in dept_ids:
                continue
            jobs.append(Job(
                title=j["title"],
                jobid=str(j["id"]),
                company="Glean",
                location=j.get("location", {}).get("name", ""),
                url=j.get("absolute_url", ""),
                posted_date=convert_to_common_format(j.get("updated_at", "")) or "",
            ))
        return jobs