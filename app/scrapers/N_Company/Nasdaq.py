from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class NasdaqScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, offset: int) -> dict:
        url = "https://nasdaq.wd1.myworkdayjobs.com/wday/cxs/nasdaq/Global_External_Site/jobs"
        payload = {
            "appliedFacets": {
                "locations": [
                    "88704065592e0167910fa64221397b91",
                    "f5b3115e55ae1002039bcb284bda0000",
                    "b638d7611d08100143bd56aa78670000",
                    "77feeca0d2d1017dd78c8be0a076211a"
                ]
            },
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Origin": "https://nasdaq.wd1.myworkdayjobs.com",
            "Referer": "https://nasdaq.wd1.myworkdayjobs.com/Global_External_Site",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("total", 0)
        all_items = list(first.get("jobPostings", []))
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_items.extend(data.get("jobPostings", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobPostings", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            ext_path = item.get("externalPath", "")
            url = f"https://nasdaq.wd1.myworkdayjobs.com/en-US/Global_External_Site{ext_path}" if ext_path else ""
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("bulletFields", [None])[0] if item.get("bulletFields") else None,
                company="Nasdaq",
                location=item.get("locationsText", item.get("location", "")),
                url=url,
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
