from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class SiemensScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.siemens-healthineers.com/api/apply/v2/jobs/563156126255251/jobs?domain=siemens.com&hl=en"

        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'jobs.siemens-healthineers.com',
            'Origin': 'jobs.siemens-healthineers.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.get(
                url, headers=headers, timeout=30)
            print(response.status_code)
            json_data = response.json()
            return json_data
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print("Response text:")
            print(
                response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        items = data.get("positions",[])
        job_list = []
        for item in items:
            job = Job(
                title=item.get("name", ""),
                jobid=item.get("id"),
                company="Siemens",
                location=item.get("location", ""),
                url=item.get("canonicalPositionUrl", ""),
                posted_date=convert_to_common_format(
                    item.get("t_update", "")),
            )
            job_list.append(job)
        return job_list
