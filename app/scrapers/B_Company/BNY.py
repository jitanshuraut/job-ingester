from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class BNYScraper(BaseScraper):
    SITE_NUMBER = "CX_3001"
    LOCATION_ID = "300000000378365"
    ORACLE_HOST = "eofe.fa.us2.oraclecloud.com"
    IRC_USERID = "03d7889c-eefa-4a84-b558-9ec498428102"

    def _build_url(self):
        base = f"https://{self.ORACLE_HOST}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
        params = (
            "onlyData=true"
            "&expand=requisitionList.workLocation"
            f"&finder=findReqs;siteNumber={self.SITE_NUMBER},"
            "facetsList=LOCATIONS,"
            "limit=200,offset=0,"
            f"locationId={self.LOCATION_ID},"
            "sortBy=POSTING_DATES_DESC"
        )
        return f"{base}?{params}"

    def _headers(self):
        return {
            'accept': '*/*',
            'content-type': 'application/vnd.oracle.adf.resourceitem+json;charset=utf-8',
            'ora-irc-cx-userid': self.IRC_USERID,
            'ora-irc-language': 'en',
            'origin': f'https://{self.ORACLE_HOST}',
            'referer': f'https://{self.ORACLE_HOST}/hcmUI/CandidateExperience/en/sites/BNY-Careers/jobs',
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
                company="BNY",
                location=location,
                url=f"https://{self.ORACLE_HOST}/hcmUI/CandidateExperience/en/sites/BNY-Careers/job/{job_id}",
                posted_date=convert_to_common_format(req.get("PostedDate", "")),
            ))
        return all_jobs
