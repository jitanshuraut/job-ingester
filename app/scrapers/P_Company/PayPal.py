from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class PayPalScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, start: int) -> dict:
        url = "https://paypal.eightfold.ai/api/pcsx/search"
        params = {
            "domain": "paypal.com",
            "query": "software",
            "location": "india",
            "start": start,
            "sort_by": "relevance",
            "filter_job_category": "Software Engineering",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://paypal.eightfold.ai/careers',
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
        count = first.get("data", {}).get("count", 0)
        all_positions = list(first.get("data", {}).get("positions", []))
        for start in range(self.PAGE_SIZE, count, self.PAGE_SIZE):
            data = self._fetch_page(start)
            all_positions.extend(data.get("data", {}).get("positions", []))
        return self._parse_positions(all_positions)

    def parse(self, data) -> list[Job]:
        return self._parse_positions(data.get("data", {}).get("positions", []))

    def _parse_positions(self, positions: list) -> list[Job]:
        job_list = []
        for item in positions:
            locations = item.get("locations", [])
            india_locations = [loc for loc in locations if "india" in loc.lower()]
            if not india_locations:
                continue
            job = Job(
                title=item.get("name", ""),
                jobid=str(item.get("id", "")),
                company="PayPal",
                location=", ".join(india_locations),
                url=f"https://paypal.eightfold.ai{item.get('positionUrl', '')}" if item.get("positionUrl") else "",
                posted_date=convert_to_common_format(item.get("postedTs")),
            )
            job_list.append(job)
        return job_list
