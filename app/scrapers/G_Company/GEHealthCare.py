import math
import requests
from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format

INDIA_KEYWORDS = "IND Bengaluru Gurgaon Guwahati Pune Mumbai Hyderabad Chennai Noida Delhi Kolkata".split()


class GEHealthCareScraper(BaseScraper):
    API_URL = "https://gehc.wd5.myworkdayjobs.com/wday/cxs/gehc/GEHC_ExternalSite/jobs"
    LIMIT = 20

    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://gehc.wd5.myworkdayjobs.com",
        "referer": "https://gehc.wd5.myworkdayjobs.com/GEHC_ExternalSite/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def _fetch_page(self, offset: int) -> dict:
        payload = {
            "appliedFacets": {},
            "limit": self.LIMIT,
            "offset": offset,
            "searchText": "",
        }
        try:
            r = requests.post(self.API_URL, json=payload, headers=self.HEADERS, timeout=30)
            return r.json()
        except Exception:
            return {}

    @staticmethod
    def _is_india(locations_text: str) -> bool:
        if not locations_text:
            return False
        for kw in INDIA_KEYWORDS:
            if kw in locations_text:
                return True
        return False

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
                loc = jp.get("locationsText") or ""
                if not self._is_india(loc):
                    continue
                title = jp.get("title", "")
                ext_path = jp.get("externalPath", "")
                req_id = (jp.get("bulletFields") or [""])[0]
                url = f"https://gehc.wd5.myworkdayjobs.com/GEHC_ExternalSite{ext_path}" if ext_path else ""
                all_jobs.append(Job(
                    title=title,
                    jobid=req_id,
                    company="GEHealthCare",
                    location=loc,
                    url=url,
                    posted_date=convert_to_common_format(jp.get("postedOn", "")),
                ))
        return all_jobs
