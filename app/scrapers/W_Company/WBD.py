from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class WBDScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, from_val: int) -> dict:
        url = "https://careers.wbd.com/widgets"
        payload = {
            "lang": "en_global",
            "deviceType": "mobile",
            "country": "global",
            "pageName": "Warner Bros. Jobs",
            "ddoKey": "eagerLoadRefineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": from_val,
            "jobs": True,
            "counts": True,
            "all_fields": ["category", "country", "state", "empType", "business", "remoteValue"],
            "pageType": "landingPage",
            "size": self.PAGE_SIZE,
            "rk": "l-warner-bros-jobs",
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": False,
            "pageId": "page84-prod",
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {"company": ["WarnerMedia"], "state": ["Karnataka"]},
            "locationData": {},
            "rkstatus": True,
            "s": "1",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://careers.wbd.com',
            'Origin': 'https://careers.wbd.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        all_items = list(first.get("data", {}).get("jobs", []))
        total = first.get("data", {}).get("total", {}).get("all", {}).get("value", 0)
        if not total:
            total = len(all_items)
        for from_val in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(from_val)
            all_items.extend(data.get("data", {}).get("jobs", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("data", {}).get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("reqId"),
                company="Warner Brother",
                location=item.get("city", ""),
                url=item.get("applyUrl", ""),
                posted_date=convert_to_common_format(item.get("postedDate", "")),
            )
            job_list.append(job)
        return job_list
