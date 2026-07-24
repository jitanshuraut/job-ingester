from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class AutodeskScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, offset: int) -> dict:
        url = "https://autodesk.wd1.myworkdayjobs.com/wday/cxs/autodesk/Ext/jobs"
        payload = {
            "appliedFacets": {
                "State_Region": [
                    "701eb5584934425d930bc84b9e8b04eb",
                    "a3c37012f51642f4a7b3dafc8ac37801",
                ],
                "jobFamilyGroup": [
                    "cebdb69fb1cc10005cc6ab3438260000",
                    "1f75c4299c9201c0f3b5f8e6fa01c5bf",
                    "cebdb69fb1cc10006a257c84e5560000",
                ],
            },
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://autodesk.wd1.myworkdayjobs.com",
            "Referer": "https://autodesk.wd1.myworkdayjobs.com/Ext",
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
            url = f"https://autodesk.wd1.myworkdayjobs.com/en-US/Ext{ext_path}" if ext_path else ""
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("bulletFields", [None])[0] if item.get("bulletFields") else None,
                company="Autodesk",
                location=item.get("locationsText", item.get("location", "")),
                url=url,
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
