from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format

class AnalogDevicesScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://analogdevices.wd1.myworkdayjobs.com/wday/cxs/analogdevices/External/jobs"

        payload = {"appliedFacets":{"timeType":["1a15e0fbb61110090028388769cb0000"],"jobFamilyGroup":["633b03df4f5d1000ec247e24e03b0000"],"locationCountry":["c4f78be1a8f14da0ab49ce1162348a5e"]},"limit":20,"offset":0,"searchText":""}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'analogdevices.wd1.myworkdayjobs.com',
            'Origin': 'analogdevices.wd1.myworkdayjobs.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.post(
                url, headers=headers,  json=payload, timeout=30)
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
        job_posts = data.get("jobPostings", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("jobId"),
                company="Amadeus",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list


if __name__ == "__main__":
    listener = AnalogDevicesScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)
