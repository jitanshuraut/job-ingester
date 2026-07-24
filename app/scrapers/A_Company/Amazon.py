from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class AmazonScraper(BaseScraper):
    PAGE_SIZE = 100

    def _fetch_page(self, offset: int) -> dict:
        url = "https://www.amazon.jobs/en-gb/search.json"
        params = {
            "category[]": "software-development",
            "schedule_type_id[]": "Full-Time",
            "normalized_country_code[]": "IND",
            "radius": "24km",
            "offset": offset,
            "result_limit": self.PAGE_SIZE,
            "sort": "relevant",
            "latitude": 28.63141,
            "longitude": 77.21676,
            "loc_query": "india",
            "base_query": "engineering",
            "country": "IND",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'www.amazon.jobs',
            'Origin': 'www.amazon.jobs',
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
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        hits = first.get("hits", 0)
        all_items = list(first.get("jobs", []))
        for offset in range(self.PAGE_SIZE, hits, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_items.extend(data.get("jobs", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id"),
                company="Amazon",
                location=item.get("normalized_location", ""),
                url=item.get("url_next_step", ""),
                posted_date=convert_to_common_format(item.get("posted_date", "")),
            )
            job_list.append(job)
        return job_list
