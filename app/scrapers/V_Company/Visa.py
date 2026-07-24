import math
import requests

from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class VisaScraper(BaseScraper):
    API_URL = "https://visa.wd5.myworkdayjobs.com/wday/cxs/visa/Visa/jobs"
    LIMIT = 20

    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://visa.wd5.myworkdayjobs.com",
        "referer": "https://visa.wd5.myworkdayjobs.com/Visa?jobFamily=2745bc1368021016a991f65e710a3b1e&locationCountry=c4f78be1a8f14da0ab49ce1162348a5e",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    FACETS = {
        "jobFamily": ["2745bc1368021016a991f65e710a3b1e"],
        "locationCountry": ["c4f78be1a8f14da0ab49ce1162348a5e"],
    }

    def _fetch_page(self, offset: int) -> dict:
        payload = {
            "appliedFacets": self.FACETS,
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
        job_postings = first.get("jobPostings") or []
        if not job_postings:
            return []
        total = first.get("total") or len(job_postings)
        total_pages = math.ceil(total / self.LIMIT)
        all_jobs = self._parse_jobs(job_postings)
        for page in range(1, total_pages):
            data = self._fetch_page(page * self.LIMIT)
            all_jobs.extend(self._parse_jobs(data.get("jobPostings") or []))
        return all_jobs

    def _parse_jobs(self, postings: list) -> list[Job]:
        jobs = []
        for jp in postings:
            title = jp.get("title", "")
            ext_path = jp.get("externalPath", "")
            location = jp.get("locationsText", "")
            req_id = (jp.get("bulletFields") or [""])[0]
            url = f"https://visa.wd5.myworkdayjobs.com/en-US/Visa{ext_path}" if ext_path else ""
            jobs.append(Job(
                title=title,
                jobid=req_id,
                company="Visa",
                location=location,
                url=url,
                posted_date=convert_to_common_format(jp.get("postedOn", "")),
            ))
        return jobs
