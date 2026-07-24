from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class CventScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, page: int) -> dict:
        url = "https://careers.cvent.com/api/jobs"
        params = {
            "tags2": "Technology|Information Technology",
            "page": page,
            "locations": "Gurugram,,India",
            "sortBy": "relevance",
            "descending": "false",
            "internal": "false",
            "domain": "cvent.jibeapply.com",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'careers.cvent.com',
            'Origin': 'careers.cvent.com',
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
        first = self._fetch_page(1)
        total_count = first.get("totalCount", 0)
        all_items = list(first.get("jobs", []))
        total_pages = max(1, -(-total_count // self.PAGE_SIZE))
        for page in range(2, total_pages + 1):
            data = self._fetch_page(page)
            all_items.extend(data.get("jobs", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            item_data = item.get("data") or {}
            job = Job(
                title=item_data.get("title", ""),
                jobid=item_data.get("req_id"),
                company="cvent",
                location=item_data.get("city", ""),
                url=item_data.get("apply_url", ""),
                posted_date=convert_to_common_format(item_data.get("posted_date", "")),
            )
            job_list.append(job)
        return job_list
