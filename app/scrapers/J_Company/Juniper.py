from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class JuniperScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, start: int) -> dict:
        url = "https://jobs.juniper.net/api/pcsx/search"
        params = {
            "domain": "juniper.net",
            "query": "",
            "location": "India",
            "start": start,
            "sort_by": "timestamp",
            "filter_include_remote": "1",
            "filter_category": "software engineering",
            "filter_seniority": "Entry",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'jobs.juniper.net',
            'Origin': 'jobs.juniper.net',
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
            job = Job(
                title=item.get("name", ""),
                jobid=item.get("id"),
                company="Juniper",
                location=item.get("location", ""),
                url=item.get("positionUrl", ""),
                posted_date=convert_to_common_format(item.get("postedTs", "")),
            )
            job_list.append(job)
        return job_list
