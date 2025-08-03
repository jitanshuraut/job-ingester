from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format

class ZSScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.zs.com/api/jobs?locations=Bengaluru,Karnataka,India%7CChennai,Tamil%20Nadu,India&page=1&tags=Architecture%20%26%20Engineering%7CBusiness%20Technology%20Solutions%7CAdvanced%20Data%20Science%7CEngineering&sortBy=posted_date&descending=true&internal=false&deviceId=undefined&domain=zs.jibeapply.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://jobs.zs.com/all/jobs',
            'Origin': 'https://jobs.zs.com/all/jobs',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url,headers=headers,timeout=30)
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
        items = data.get("jobs",[])
        job_list = []
        for item in items:
            job = Job(
                title=item.get("data").get("title", ""),
                jobid=item.get("data").get("req_id"),
                company="ZS",
                location=item.get("data").get("location_name", ""),
                url=item.get("data").get("apply_url", ""),
                posted_date=convert_to_common_format(item.get("data").get("update_date", ""))
            )
            job_list.append(job)
        return job_list



