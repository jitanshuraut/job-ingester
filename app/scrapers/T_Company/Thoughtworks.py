from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class ThoughtworksScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://www.thoughtworks.com/rest/careers/jobs"

        

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'www.thoughtworks.com',
            'Origin': 'www.thoughtworks.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url, headers=headers, timeout=30)
            json_data = response.json()
            print(response.status_code)
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
        job_posts = data.get("jobs", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("name", ""),
                jobid=item.get("sourceSystemId"),
                company="Thoughtworks",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("updatedAt", "")),
            )
            job_list.append(job)
        return job_list
