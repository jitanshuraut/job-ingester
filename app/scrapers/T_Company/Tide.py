from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API = "https://boards-api.greenhouse.io/v1/boards/tide/jobs"

OFFICES = {
    "bengaluru": 4052091003,
    "delhi": 4052072003,
    "hyderabad": 4052071003,
    "india": 4052070003,
    "london": 4052076003,
    "berlin": 4052074003,
    "bulgaria": 4052078003,
    "romania": 4052082003,
    "ukraine": 4052088003,
}

DEPARTMENTS = {
    "engineering": "Engineering",
    "data & analytics": "Data & Analytics",
    "product & design": "Product & Design",
    "finance": "Finance",
    "risk & compliance": "Risk & Compliance",
    "legal": "Legal",
    "commercial": "Commercial",
}


class TideScraper(BaseScraper):
    OFFICE_ID = OFFICES["india"]
    DEPARTMENT_NAME = DEPARTMENTS["engineering"]

    def fetch_raw(self):
        resp = requests.get(API, params={"content": "true"}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("jobs", [])

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            location = j.get("location", {}).get("name", "")
            office_ids = [o["id"] for o in j.get("offices", [])]
            dept_names = []
            for m in j.get("metadata", []):
                if m["id"] == 5671766003:
                    vals = m.get("value", [])
                    dept_names = vals if isinstance(vals, list) else [vals]
            if self.OFFICE_ID and self.OFFICE_ID not in office_ids:
                continue
            if self.DEPARTMENT_NAME and self.DEPARTMENT_NAME not in dept_names:
                continue
            jobs.append(Job(
                title=j["title"],
                jobid=str(j["id"]),
                company="Tide",
                location=location,
                url=j.get("absolute_url", ""),
                posted_date=convert_to_common_format(j.get("updated_at", "")) or "",
            ))
        return jobs