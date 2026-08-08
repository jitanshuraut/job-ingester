from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests

API = "https://api.pyjamahr.com/api/career/jobs/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://app.pyjamahr.com",
    "Referer": "https://app.pyjamahr.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36",
    "X-Client-Fingerprint": "d7ffbaef531f343a11dd72ec3d94095ea9cd1afa458fc86c04c8927693d44892",
    "X-Fingerprint-Version": "4",
}


class ZocaScraper(BaseScraper):
    COMPANY_UUID = "6FFECB46A0"

    def fetch_raw(self):
        all_jobs = []
        page = 1
        while True:
            params = {
                "company_uuid": self.COMPANY_UUID,
                "page": page,
                "is_careers_page": "true",
            }
            resp = requests.get(API, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            all_jobs.extend(data["results"])
            if not data.get("next"):
                break
            page += 1
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for j in raw:
            jobs.append(Job(
                title=j["title"],
                jobid=str(j["id"]),
                company="Zoca",
                location=j.get("location", ""),
                url=f"https://app.pyjamahr.com/careers/{self.COMPANY_UUID}/job/{j['id']}",
                posted_date="",
            ))
        return jobs