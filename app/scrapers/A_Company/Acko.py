from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format

class AckoScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, offset: int) -> dict:
        url = "https://acko.sensehq.in/careers/api/postings"
        params = {
            'offset': offset,
            'limit': self.PAGE_SIZE,
            'location': '',
            'department': 'Technology - Engineering - Central - Dev (Backend/Frontend/Mobile)'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.acko.com',
            'Origin': 'https://www.acko.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        all_items = list(first.get("content", []))
        total = first.get("totalElements") or first.get("totalPages", 0) * self.PAGE_SIZE
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_items.extend(data.get("content", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("content", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id"),
                company="Acko",
                location=item.get("location", ""),
                url=item.get("link", ""),
                posted_date=convert_to_common_format(datetime.utcfromtimestamp(item.get("updated_on", 0) / 1000))
            )
            job_list.append(job)
        return job_list
