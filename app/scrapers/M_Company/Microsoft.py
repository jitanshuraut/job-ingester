from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class MicrosoftScraper(BaseScraper):
    PAGE_SIZE = 10

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def _fetch_page(self, start: int) -> dict:
        params = {
            "domain": "microsoft.com",
            "query": "software",
            "location": "india",
            "start": start,
            "sort_by": "relevance",
            "filter_include_remote": 1,
        }
        try:
            response = self._session.get(
                "https://apply.careers.microsoft.com/api/pcsx/search",
                params=params, timeout=30,
            )
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
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
            std_locs = item.get("standardizedLocations", [])
            location = std_locs[0] if std_locs else (item.get("locations", [""])[0])
            if not location:
                continue
            job = Job(
                title=item.get("name", ""),
                jobid=str(item.get("id", "")),
                company="Microsoft",
                location=location,
                url=f"https://apply.careers.microsoft.com{item.get('positionUrl', '')}" if item.get("positionUrl") else "",
                posted_date=convert_to_common_format(item.get("postedTs")),
            )
            job_list.append(job)
        return job_list
