from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class AdobeScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://careers.adobe.com/widgets"

        payload = {
            "lang": "en_us",
            "deviceType": "mobile",
            "country": "us",
            "pageName": "Engineering and Product jobs",
            "ddoKey": "refineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": 0,
            "jobs": True,
            "counts": True,
            "all_fields": [
                    "remote",
                    "country",
                    "state",
                    "city",
                    "experienceLevel",
                    "category",
                    "profession",
                    "employmentType",
                    "jobLevel"
            ],
            "pageType": "category",
            "size": 200,
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": False,
            "pageId": "page62-ds",
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {
                "category": [
                        "Engineering and Product"
                ],
                "country": [
                    "India"
                ],
                "jobLevel": [
                    "Individual Contributor"
                ]
            },
            "locationData": {}
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://careers.adobe.com/',  
            'Origin': 'https://careers.adobe.com',   
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
        job_posts = data.get("refineSearch", {}).get("data",{}).get("jobs",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("jobId"),
                company="Adobe",
                location=item.get("location", ""),
                url=item.get("applyUrl", ""),
                posted_date=convert_to_common_format(item.get("postedDate", "")),
            )
            job_list.append(job)
        return job_list



