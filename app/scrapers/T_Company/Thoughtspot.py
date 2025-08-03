from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class ThoughtspotScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://thoughtspot.wd5.myworkdayjobs.com/wday/cxs/thoughtspot/careers/jobs"

        payload = {"appliedFacets":{"locations":["939fa72d127c102407551371b40d0000","939fa72d127c102407550c3724bc0000"],"jobFamilyGroup":["a925daa791b71000f87f035c7ae20000"]},"limit":20,"offset":0,"searchText":""}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'thoughtspot.wd5.myworkdayjobs.com',
            'Origin': 'thoughtspot.wd5.myworkdayjobs.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.post(
                url, headers=headers,  json=payload, timeout=30)
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
        job_posts = data.get("jobPostings", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("jobId"),
                company="Thoughtspot",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
