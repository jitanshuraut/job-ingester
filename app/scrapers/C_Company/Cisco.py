from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class CiscoScraper(BaseScraper):
    PAGE_SIZE = 50

    def _build_payload(self, offset: int) -> dict:
        return {
            "lang": "en_global",
            "deviceType": "desktop",
            "country": "global",
            "pageName": "search-results",
            "ddoKey": "refineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": offset,
            "jobs": True,
            "counts": True,
            "all_fields": ["category", "country", "state", "city", "type", "RemoteType"],
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

    def fetch_jobs(self) -> list[Job]:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://careers.cisco.com",
            "Referer": "https://careers.cisco.com/global/en/search-results",
        }

        try:
            r = requests.post("https://careers.cisco.com/widgets", json=self._build_payload(0), headers=headers, timeout=30)
            data = r.json()
        except (json.JSONDecodeError, requests.RequestException):
            return []

        rs = data.get("refineSearch", {})
        total = rs.get("totalHits", 0)
        all_jobs = list(rs.get("data", {}).get("jobs", []))

        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            try:
                r = requests.post("https://careers.cisco.com/widgets", json=self._build_payload(offset), headers=headers, timeout=30)
                all_jobs.extend(r.json().get("refineSearch", {}).get("data", {}).get("jobs", []))
            except (json.JSONDecodeError, requests.RequestException):
                break

        job_list = []
        for j in all_jobs:
            city = j.get("city", "") or ""
            state = j.get("state", "") or ""
            location = f"{city}, {state}".strip(", ")
            if not location:
                location = "India"
            job_list.append(Job(
                title=j.get("title", ""),
                jobid=j.get("jobId"),
                company="Cisco",
                location=location,
                url=j.get("applyUrl", j.get("url", "")),
                posted_date=convert_to_common_format(j.get("postedDate", "")),
            ))
        return job_list
