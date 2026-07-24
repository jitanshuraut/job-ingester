from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class SalesforceScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, offset: int) -> dict:
        url = "https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs"
        payload = {
            "appliedFacets": {
                "locations": [
                    "2c2bf80869591012453ab08dba870000",
                    "8ef61f627eb01012453a9ce004d20000",
                    "1038e944b11010124539eb4950f50000",
                    "1038e944b1101012453f5b10dc370000",
                ],
                "jobFamilyGroup": ["14fa3452ec7c1011f90d0002a2100000"],
            },
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://salesforce.wd12.myworkdayjobs.com',
            'Referer': 'https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site',
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(response.status_code)
        return response.json()

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("total", 0)
        all_items = list(first.get("jobPostings", []))
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            try:
                data = self._fetch_page(offset)
                all_items.extend(data.get("jobPostings", []))
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed to fetch offset {offset}")
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobPostings", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("bulletFields")[0],
                company="Salesforce",
                location=item.get("locationsText", ""),
                url=f"https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site{item.get('externalPath', '')}" if item.get("externalPath") else "",
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
