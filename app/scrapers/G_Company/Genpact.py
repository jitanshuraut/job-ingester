from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class GenpactScraper(BaseScraper):
    PAGE_SIZE = 20
    API_URL = "https://genpact.wd108.myworkdayjobs.com/wday/cxs/genpact/External_Careers/jobs"
    TECH_FAMILY_ID = "faddece16d451000bc553ead44380000"

    def _fetch_page(self, offset: int) -> dict:
        payload = {
            "appliedFacets": {"jobFamilyGroup": [self.TECH_FAMILY_ID]},
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("total", 0)
        all_items = []
        for item in first.get("jobPostings", []):
            if "India" in item.get("locationsText", ""):
                all_items.append(item)
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            for item in data.get("jobPostings", []):
                if "India" in item.get("locationsText", ""):
                    all_items.append(item)
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        items = data.get("jobPostings", [])
        return self._parse_items(items)

    @staticmethod
    def _clean_location(locations_text: str) -> str:
        parts = locations_text.split(":")
        if len(parts) > 1:
            return parts[1].strip()
        return locations_text

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            loc = item.get("locationsText", "")
            if "India" not in loc:
                continue
            ext_path = item.get("externalPath", "")
            full_url = f"https://genpact.wd108.myworkdayjobs.com{ext_path}" if ext_path.startswith("/") else ext_path
            bullet = item.get("bulletFields", [])
            job_id = bullet[0] if bullet else ""
            job = Job(
                title=item.get("title", ""),
                jobid=job_id,
                company="Genpact",
                location=self._clean_location(loc),
                url=full_url,
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
