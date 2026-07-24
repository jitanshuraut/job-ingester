from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
from app.utils.DateConverter import convert_to_common_format

class AirtelLabsScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, page: int) -> dict:
        url = "https://airtel.darwinbox.in/ms/candidateapi/job?department=a66b91c788be2d&exp_from=1"
        params = {"page": page, "limit": self.PAGE_SIZE}
        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://airtel.darwinbox.in/ms/candidate/careers',
            'Origin': 'https://airtel.darwinbox.in/ms/candidate/careers',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(1)

    def fetch_jobs(self) -> list[Job]:
        all_items = []
        page = 1
        while True:
            data = self._fetch_page(page)
            items = data.get("message", {}).get("jobs", [])
            if not items:
                break
            all_items.extend(items)
            page += 1
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("message", {}).get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("designation_display_name", ""),
                jobid=item.get("id"),
                company="AirtelLabs",
                location=item.get("officelocation_show_arr", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("created_on", "")),
            )
            job_list.append(job)
        return job_list
