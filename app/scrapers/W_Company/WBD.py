from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class WBDScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://careers.wbd.com/widgets"

        payload = {
            "lang": "en_global",
            "deviceType": "mobile",
            "country": "global",
            "pageName": "Warner Bros. Jobs",
            "ddoKey": "eagerLoadRefineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": 0,
            "jobs": True,
            "counts": True,
            "all_fields": [
                "category", "country", "state", "empType", "business", "remoteValue"
            ],
            "pageType": "landingPage",
            "size": 10,
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
            "s": "1"
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
            'Pragma': 'no-cache'
        }
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=30)
            print(response.status_code)
            json_data = response.json()
            return json_data
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print("Response text:")
            print(
                response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        items = data.get("data", {}).get("jobs", [])
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("reqId"),
                company="Warner Brother",
                location=item.get("city", ""),
                url=item.get("applyUrl", ""),
                posted_date=convert_to_common_format(
                    item.get("postedDate", "")),
            )
            job_list.append(job)
        return job_list
