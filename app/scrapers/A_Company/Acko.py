from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.analyzer.extractor import analyze_job_description
import requests
import json
import re
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format

class AckoScraper(BaseScraper):
    BASE_URL = "https://careers.kula.ai/api/internal/ats_job_posts"
    PAGE_SIZE = 99
    DEPARTMENT_ID = 4196

    def _fetch_page(self, page: int) -> dict:
        params = {
            'accountName': 'acko',
            'page': page,
            'filter_by[ats_department_ids][]': self.DEPARTMENT_ID,
            'type': 'ats_job_post.index',
            'items': self.PAGE_SIZE,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://careers.kula.ai/acko?jobs=true',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(1)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(1)
        all_items = list(first.get("data", []))
        total_pages = first.get("meta", {}).get("pages", 1)
        for page in range(2, total_pages + 1):
            data = self._fetch_page(page)
            all_items.extend(data.get("data", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("data", []))

    @staticmethod
    def _strip_html(html: str) -> str:
        if not html:
            return ""
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            ats_job = item.get("ats_job") or {}
            offices = ats_job.get("offices") or []
            locations = ", ".join(o.get("location", "") for o in offices if o.get("location"))
            department = (ats_job.get("ats_department") or {}).get("name", "")
            description = self._strip_html(ats_job.get("job_description", ""))
            analysis = analyze_job_description(description)
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id")),
                company="Acko",
                location=locations,
                url=f"https://careers.kula.ai/acko/jobs/{item.get('id')}",
                posted_date=convert_to_common_format(datetime.now()),
                experience_years=json.dumps(analysis["experience_years"]),
                skills=json.dumps(analysis["skills"]),
            )
            job_list.append(job)
        return job_list
