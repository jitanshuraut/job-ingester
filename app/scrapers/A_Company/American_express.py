from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class AmericanExpressScraper(BaseScraper):
    LOCATION_ID = "300000000228786"

    def _build_url(self):
        base = "https://egug.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
        params = (
            "onlyData=true"
            "&expand=requisitionList.workLocation"
            "&finder=findReqs;siteNumber=CX_1,"
            "facetsList=LOCATIONS,"
            "limit=200,offset=0,"
            f"locationId={self.LOCATION_ID},"
            "sortBy=POSTING_DATES_DESC"
        )
        return f"{base}?{params}"

    def _headers(self):
        return {
            'accept': '*/*',
            'accept-language': 'en',
            'content-type': 'application/vnd.oracle.adf.resourceitem+json;charset=utf-8',
            'ora-irc-cx-userid': 'f9328128-e87c-429f-bdb0-74e35921563b',
            'ora-irc-language': 'en',
            'origin': 'https://careers.americanexpress.com',
            'referer': 'https://careers.americanexpress.com/',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        }

    def fetch_jobs(self) -> list[Job]:
        try:
            r = requests.get(self._build_url(), headers=self._headers(), timeout=30)
            data = r.json()
            items = data.get("items", [])
            if not items:
                return []
            reqs = items[0].get("requisitionList", [])
        except (json.JSONDecodeError, requests.RequestException, IndexError, KeyError):
            return []

        all_jobs = []
        for req in reqs:
            title = req.get("Title", "")
            job_id = str(req.get("Id", ""))
            if not title or not job_id:
                continue
            location = req.get("PrimaryLocation") or "India"
            all_jobs.append(Job(
                title=title,
                jobid=job_id,
                company="AmericanExpress",
                location=location,
                url=f"https://careers.americanexpress.com/en/job/{job_id}/",
                posted_date=convert_to_common_format(req.get("PostedDate", "")),
            ))
        return all_jobs
