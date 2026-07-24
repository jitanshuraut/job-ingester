from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class FICOScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, offset: int) -> dict:
        url = "https://fico.wd1.myworkdayjobs.com/wday/cxs/fico/External/jobs"
        payload = {
            "appliedFacets": {"locations": ["a46e175d937b106cf81d43a54c42fa46", "a46e175d937b106cf81e3390fa9bfb99"], "jobFamilyGroup": ["a46e175d937b106cdb2f901ef52e94e9", "a46e175d937b106cdb2fbd87114194f5"]},
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
            "Referer": "fico.wd1.myworkdayjobs.com",
            "Origin": "fico.wd1.myworkdayjobs.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
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
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("jobId"),
                company="FICO",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
