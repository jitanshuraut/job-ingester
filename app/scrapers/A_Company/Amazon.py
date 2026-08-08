from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.analyzer.extractor import analyze_job_description
import requests
import json
import re
from app.utils.DateConverter import convert_to_common_format

class AmazonScraper(BaseScraper):
    PAGE_SIZE = 5

    def _build_params(self, offset: int) -> dict:
        return {
            "category[]": "software-development",
            "radius": "100000km",
            "industry_experience[]": "one_to_three_years",
            "facets[]": [
                "normalized_country_code", "normalized_state_name", "normalized_city_name",
                "location", "business_category", "category", "schedule_type_id",
                "employee_class", "normalized_location", "job_function_id",
                "is_manager", "is_intern",
            ],
            "offset": offset,
            "result_limit": self.PAGE_SIZE,
            "sort": "relevant",
            "latitude": 28.63141,
            "longitude": 77.21676,
            "loc_group_id": "",
            "loc_query": "india",
            "base_query": "",
            "city": "",
            "country": "IND",
            "region": "",
            "county": "",
            "query_options": "",
        }

    def _headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.jobs/en/search?offset=0&result_limit=10&sort=relevant&category%5B%5D=software-development&distanceType=Mi&radius=Anykm&industry_experience=one_to_three_years&latitude=28.63141&longitude=77.21676&loc_group_id=&loc_query=india&base_query=&city=&country=IND&region=&county=&query_options=&',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    def _fetch_page(self, offset: int) -> dict:
        try:
            response = requests.get(
                "https://www.amazon.jobs/en/search.json",
                params=self._build_params(offset),
                headers=self._headers(),
                timeout=30,
            )
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

    @staticmethod
    def _strip_html(text: str) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            bq = self._strip_html(item.get("basic_qualifications", ""))
            desc = self._strip_html(item.get("description", ""))
            analysis = analyze_job_description(f"{bq}\n{desc}")
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id_icims") or item.get("id"),
                company="Amazon",
                location=item.get("normalized_location", ""),
                url="https://www.amazon.jobs" + item.get("job_path", ""),
                posted_date=convert_to_common_format(item.get("posted_date", "")),
                experience_years=json.dumps(analysis["experience_years"]),
                skills=json.dumps(analysis["skills"]),
            )
            job_list.append(job)
        return job_list
