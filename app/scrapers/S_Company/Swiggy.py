from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class SwiggyScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://swiggy.mynexthire.com/employer/careers/reqlist/get"
        payload = {
            "source": "careers",
            "code": "",
            "filterByBuId": -1,
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://swiggy.mynexthire.com",
            "Referer": "https://swiggy.mynexthire.com/employer/jobs/careers",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def parse(self, data) -> list[Job]:
        items = data.get("reqDetailsBOList", []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            return []
        job_list = []
        for item in items:
            req_id = item.get("reqId", "")
            job = Job(
                title=item.get("reqTitle", ""),
                jobid=str(req_id),
                company="Swiggy",
                location=item.get("location", ""),
                url=f"https://swiggy.mynexthire.com/employer/jobs/careers?jobId={req_id}" if req_id else "",
                posted_date=convert_to_common_format(item.get("approvedOn", "")),
            )
            job_list.append(job)
        return job_list
