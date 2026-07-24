from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class HPEScraper(BaseScraper):
    PAGE_SIZE = 200

    def _build_payload(self, from_val: int) -> dict:
        return {
            "lang": "en_us",
            "deviceType": "desktop",
            "country": "us",
            "pageName": "search-results",
            "ddoKey": "refineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": from_val,
            "jobs": True,
            "counts": True,
            "all_fields": ["country", "state", "city", "category"],
            "size": self.PAGE_SIZE,
            "pageType": "searchResults",
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": False,
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {"country": ["India"]},
            "locationData": {},
            "rkstatus": True,
        }

    def fetch_raw(self):
        try:
            r = requests.post(
                "https://careers.hpe.com/widgets",
                json=self._build_payload(0),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Content-Type": "application/json",
                    "Origin": "https://careers.hpe.com",
                    "Referer": "https://careers.hpe.com/us/en/c/engineering-qa-jobs",
                },
                timeout=30,
            )
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data: dict) -> list[Job]:
        rs = data.get("refineSearch", {})
        jobs_data = rs.get("data", {}).get("jobs", [])
        total = rs.get("totalHits", len(jobs_data))
        all_jobs = list(jobs_data)
        for from_val in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            try:
                r = requests.post(
                    "https://careers.hpe.com/widgets",
                    json=self._build_payload(from_val),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Content-Type": "application/json",
                        "Origin": "https://careers.hpe.com",
                        "Referer": "https://careers.hpe.com/us/en/c/engineering-qa-jobs",
                    },
                    timeout=30,
                )
                page = r.json()
                all_jobs.extend(page.get("refineSearch", {}).get("data", {}).get("jobs", []))
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed at from={from_val}")
        job_list = []
        for j in all_jobs:
            city = j.get("city", "") or ""
            state = j.get("state", "") or ""
            location = f"{city}, {state}".strip(", ")
            job = Job(
                title=j.get("title", ""),
                jobid=j.get("jobId"),
                company="HPE",
                location=location,
                url=j.get("applyUrl", "") or "",
                posted_date=convert_to_common_format(j.get("postedDate", "")),
            )
            job_list.append(job)
        return job_list
