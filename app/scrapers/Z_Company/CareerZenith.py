from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class CareerZenithScraper(BaseScraper):
    PAGE_SIZE = 12

    def _fetch_page(self, page: int) -> dict:
        url = "https://api.careerzenith.ai/job-board/user/"
        params = {"page_size": self.PAGE_SIZE, "page": page}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://careerzenith.ai',
            'Referer': 'https://careerzenith.ai/',
        }
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(response.status_code)
        return response.json()

    def fetch_raw(self):
        return self._fetch_page(1)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(1)
        if not first.get("jobs"):
            return []
        total_pages = first.get("total_pages", 1)
        all_items = list(first.get("jobs", []))
        for page in range(2, total_pages + 1):
            try:
                data = self._fetch_page(page)
                all_items.extend(data.get("jobs", []))
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed to fetch page {page}")
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            company_data = item.get("company") or {}
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id", "")),
                company=company_data.get("name", "CareerZenith"),
                location=item.get("location", ""),
                url=item.get("url", ""),
                posted_date=item.get("updated_at", ""),
            )
            job_list.append(job)
        return job_list
