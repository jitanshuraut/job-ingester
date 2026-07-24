from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class QualcommScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, start: int) -> dict:
        url = "https://careers.qualcomm.com/api/pcsx/search"
        params = {
            "domain": "qualcomm.com",
            "query": "",
            "location": "india",
            "start": start,
            "sort_by": "distance",
            "filter_job_family": "software engineering",
            "filter_seniority": ["Entry", "Mid-Level", "Intern"],
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://careers.qualcomm.com/careers',
        }
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(response.status_code)
        return response.json()

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        count = first.get("data", {}).get("count", 0)
        all_positions = list(first.get("data", {}).get("positions", []))
        for start in range(self.PAGE_SIZE, count, self.PAGE_SIZE):
            try:
                data = self._fetch_page(start)
                all_positions.extend(data.get("data", {}).get("positions", []))
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed to fetch start={start}")
        return self._parse_positions(all_positions)

    def parse(self, data) -> list[Job]:
        return self._parse_positions(data.get("data", {}).get("positions", []))

    def _parse_positions(self, positions: list) -> list[Job]:
        job_list = []
        for item in positions:
            location = item.get("locations", [])
            job = Job(
                title=item.get("name", ""),
                jobid=str(item.get("id", "")),
                company="Qualcomm",
                location=location[0] if location else "",
                url=f"https://careers.qualcomm.com{item.get('positionUrl', '')}" if item.get("positionUrl") else "",
                posted_date=convert_to_common_format(item.get("postedTs")),
            )
            job_list.append(job)
        return job_list
