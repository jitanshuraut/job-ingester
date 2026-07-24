from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import math


class NvidiaScraper(BaseScraper):
    API_URL = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"
    LIMIT = 20

    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://nvidia.wd5.myworkdayjobs.com",
        "referer": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def _request(self, offset: int) -> dict:
        payload = {
            "appliedFacets": {
                "locationHierarchy1": ["2fcb99c455831013ea52b82135ba3266"],
                "jobFamilyGroup": ["0c40f6bd1d8f10ae43ffaefd46dc7e78"],
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
        first = self._request(0)
        total = first.get("total") or 0
        if not total:
            return []
        total_pages = math.ceil(total / self.LIMIT)
        jobs = []
        for page in range(total_pages):
            data = self._request(page * self.LIMIT) if page > 0 else first
            for jp in data.get("jobPostings") or []:
                title = jp.get("title", "")
                if not title:
                    continue
                ext_path = jp.get("externalPath", "")
                req_id = (jp.get("bulletFields") or [""])[0]
                url = f"https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite{ext_path}" if ext_path else ""
                jobs.append(Job(
                    title=title,
                    jobid=req_id,
                    company="NVIDIA",
                    location=jp.get("locationsText", ""),
                    url=url,
                    posted_date=convert_to_common_format(jp.get("postedOn", "")),
                ))
        return jobs
