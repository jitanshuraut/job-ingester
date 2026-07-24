from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import math


class RedHatScraper(BaseScraper):
    API_URL = "https://redhat.wd5.myworkdayjobs.com/wday/cxs/redhat/Jobs/jobs"
    LIMIT = 20

    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://redhat.wd5.myworkdayjobs.com",
        "referer": "https://redhat.wd5.myworkdayjobs.com/Jobs",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    INDIA_KEYWORDS = [
        "India", "Bangalore", "Pune", "Mumbai",
        "Gurgaon", "Hyderabad", "Chennai", "Noida", "Kolkata", "Delhi",
    ]

    def _request(self, offset: int) -> dict:
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

    def _is_india(self, location: str) -> bool:
        if not location:
            return False
        for kw in self.INDIA_KEYWORDS:
            if kw.lower() in location.lower():
                return True
        return False

    def fetch_jobs(self) -> list[Job]:
        first = self._request(0)
        total = first.get("total") or 0
        if not total:
            return []
        total_pages = math.ceil(total / self.LIMIT)
        all_jobs = []
        for page in range(total_pages):
            data = self._request(page * self.LIMIT) if page > 0 else first
            for jp in data.get("jobPostings") or []:
                loc = jp.get("locationsText", "")
                if not self._is_india(loc):
                    continue
                title = jp.get("title", "")
                if not title:
                    continue
                ext_path = jp.get("externalPath", "")
                req_id = (jp.get("bulletFields") or [""])[0]
                url = f"https://redhat.wd5.myworkdayjobs.com/Jobs{ext_path}" if ext_path else ""
                all_jobs.append(Job(
                    title=title,
                    jobid=req_id,
                    company="Red Hat",
                    location=loc,
                    url=url,
                    posted_date=convert_to_common_format(jp.get("postedOn", "")),
                ))
        return all_jobs
