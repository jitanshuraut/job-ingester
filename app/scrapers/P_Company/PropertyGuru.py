from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import math


class PropertyGuruScraper(BaseScraper):
    API_URL = "https://propertyguru.wd105.myworkdayjobs.com/wday/cxs/propertyguru/PropertyGuru/jobs"
    LIMIT = 20

    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://propertyguru.wd105.myworkdayjobs.com",
        "referer": "https://propertyguru.wd105.myworkdayjobs.com/PropertyGuru",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def _fetch_page(self, offset: int) -> dict:
        payload = {
            "appliedFacets": {
                "locations": ["8ddf56e76fde1005210b476f4bff0000"]
            },
            "limit": self.LIMIT,
            "offset": offset,
            "searchText": "",
        }
        try:
            r = requests.post(self.API_URL, json=payload, headers=self.HEADERS, timeout=30)
            return r.json()
        except Exception:
            return {}

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("total") or 0
        if not total:
            return []
        total_pages = math.ceil(total / self.LIMIT)
        all_jobs = []
        for page in range(total_pages):
            data = self._fetch_page(page * self.LIMIT) if page > 0 else first
            for jp in data.get("jobPostings") or []:
                title = jp.get("title", "")
                if not title:
                    continue
                ext_path = jp.get("externalPath", "")
                req_id = (jp.get("bulletFields") or [""])[0]
                url = f"https://propertyguru.wd105.myworkdayjobs.com/PropertyGuru{ext_path}" if ext_path else ""
                all_jobs.append(Job(
                    title=title,
                    jobid=req_id,
                    company="PropertyGuru",
                    location=jp.get("locationsText", ""),
                    url=url,
                    posted_date=convert_to_common_format(jp.get("postedOn", "")),
                ))
        return all_jobs
