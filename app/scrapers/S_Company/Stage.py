from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

EMBED_URL = "https://job-boards.greenhouse.io/embed/job_board"

HEADERS = {
    "accept": "*/*",
    "referer": "https://job-boards.greenhouse.io/embed/job_board?for=stage",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36",
}

BOARD = "stage"

OFFICES = {
    "australia": 4003428004,
    "hong kong": 4003415004,
    "india": 4003426004,
    "japan": 4003420004,
    "singapore": 4003409004,
    "bermuda": 4110607004,
    "united states": 4003379004,
    "united states remote": 4046322004,
    "england": 4003394004,
    "ireland": 4003392004,
}

DEPARTMENTS = {
    "technology": 4007025004,
    "next generation technology": 4006987004,
    "finance": 4006315004,
    "operations": 4006344004,
    "risk": 4006892004,
    "legal": 4006983004,
    "product": 4006997004,
}


class StageScraper(BaseScraper):
    OFFICE_IDS = [OFFICES["india"]]
    DEPT_IDS = [DEPARTMENTS["technology"]]

    def fetch_raw(self):
        all_jobs = []
        page = 1
        total_pages = 1
        while page <= total_pages:
            params = {"for": BOARD, "_data": "routes/embed.job_board", "page": page}
            if self.OFFICE_IDS:
                params["offices[]"] = self.OFFICE_IDS
            if self.DEPT_IDS:
                params["departments[]"] = self.DEPT_IDS
            resp = requests.get(EMBED_URL, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            jp = data["jobPosts"]
            total_pages = jp["total_pages"]
            all_jobs.extend(jp["data"])
            page += 1
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            dept = j.get("department", {})
            jobs.append(Job(
                title=j["title"],
                jobid=str(j["id"]),
                company="Stage",
                location=j.get("location", ""),
                url=j.get("absolute_url", ""),
                posted_date=convert_to_common_format(j.get("updated_at", "")) or "",
            ))
        return jobs