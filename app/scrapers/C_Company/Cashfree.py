from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class CashfreeScraper(BaseScraper):
    PAGE_SIZE = 99

    def _fetch_page(self, page: int) -> dict:
        url = "https://careers.kula.ai/api/internal/ats_job_posts"
        params = {
            "accountName": "cashfree",
            "page": page,
            "filter_by[ats_department_ids][]": 2613,
            "type": "ats_job_post.index",
            "items": self.PAGE_SIZE,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://careers.kula.ai/cashfree?jobs=true',
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
            items = data.get("data", [])
            if not items:
                break
            all_items.extend(items)
            page += 1
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("data", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            ats = item.get("ats_job") or {}
            offices = ats.get("offices") or []
            location = offices[0].get("location", "India") if offices else "India"
            title = item.get("title", "")
            job_id = item.get("id")
            job_list.append(Job(
                title=title,
                jobid=str(job_id) if job_id else None,
                company="CashFree",
                location=location,
                url=f"https://careers.kula.ai/cashfree/jobs/{job_id}" if job_id else "",
                posted_date="",
            ))
        return job_list
