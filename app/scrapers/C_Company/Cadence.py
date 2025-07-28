from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class CadenceScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://cadence.wd1.myworkdayjobs.com/wday/cxs/cadence/External_Careers/jobs"

        payload = {"appliedFacets": {"locations": ["6418637d4d5010bf8a99bda155db6142", "d1bbeffd71a2100121c577c184b10000", "6418637d4d5010bf8a99b84a103c613d", "99daf6c35e5010011f3a4faaf3320000", "6418637d4d5010bf8a99b21035266138", "84b6cfd69db310b0db9d79bf33759a36",
                                                   "6418637d4d5010bf8a99a4926e59612e", "6418637d4d5010bf8a99abd03be56133"], "timeType": ["59ec2ade908946248e84acbf58584a93"], "Location_Country": ["c4f78be1a8f14da0ab49ce1162348a5e"]}, "limit": 20, "offset": 0, "searchText": ""}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'cadence.wd1.myworkdayjobs.com',
            'Origin': 'cadence.wd1.myworkdayjobs.com',
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
                company="Cadence",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
