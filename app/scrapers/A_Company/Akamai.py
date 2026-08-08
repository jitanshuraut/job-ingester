from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.analyzer.extractor import analyze_job_description
import requests
import json
import re
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class AkamaiScraper(BaseScraper):
    BASE_URL = "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest"
    LIMIT = 25

    def _build_url(self, offset: int) -> str:
        finder = (f"findReqs;siteNumber=CX_1,"
                  f"facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,"
                  f"limit={self.LIMIT},lastSelectedFacet=TITLES,"
                  f"selectedLocationsFacet=300000000469285,selectedTitlesFacet=ENG,"
                  f"sortBy=POSTING_DATES_DESC")
        return (f"{self.BASE_URL}/recruitingCEJobRequisitions?"
                f"onlyData=true&"
                f"expand=requisitionList.workLocation,requisitionList.otherWorkLocations,"
                f"requisitionList.secondaryLocations,flexFieldsFacet.values,"
                f"requisitionList.requisitionFlexFields&"
                f"finder={finder}&offset={offset}")

    def _headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en',
            'Content-Type': 'application/vnd.oracle.adf.resourceitem+json;charset=utf-8',
            'ora-irc-cx-userid': '27428873-7eb7-46fb-880f-bfa1b9750678',
            'ora-irc-language': 'en',
            'Origin': 'https://jobs.akamai.com',
            'Referer': 'https://jobs.akamai.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    def _fetch_page(self, offset: int) -> dict:
        try:
            response = requests.get(self._build_url(offset), headers=self._headers(), timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        all_items = self._requisition_list(first)
        total = self._total_jobs(first)
        for offset in range(self.LIMIT, total, self.LIMIT):
            data = self._fetch_page(offset)
            all_items.extend(self._requisition_list(data))
        return self._parse_items(all_items)

    @staticmethod
    def _requisition_list(data: dict) -> list:
        items = data.get("items", [])
        if not items:
            return []
        return items[0].get("requisitionList", [])

    @staticmethod
    def _total_jobs(data: dict) -> int:
        items = data.get("items", [])
        if not items:
            return 0
        return items[0].get("TotalJobsCount") or 0

    def parse(self, data) -> list[Job]:
        return self._parse_items(self._requisition_list(data))

    def _fetch_description(self, job_id: str) -> str:
        url = (f"{self.BASE_URL}/recruitingCEJobRequisitionDetails/{job_id}"
               f"?onlyData=true&expand=all")
        try:
            response = requests.get(url, headers=self._headers(), timeout=30)
            data = response.json()
            html = data.get("ExternalDescriptionStr", "")
            text = re.sub(r"<[^>]+>", " ", html)
            return re.sub(r"\s+", " ", text).strip()
        except (json.JSONDecodeError, requests.RequestException, KeyError):
            return ""

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            work_location = item.get("workLocation") or []
            location = work_location[0].get("TownOrCity", "") if work_location else ""
            description = self._fetch_description(str(item.get("Id")))
            analysis = analyze_job_description(description)
            job = Job(
                title=item.get("Title", ""),
                jobid=item.get("Id"),
                company="Akamai",
                location=location,
                url=f"https://jobs.akamai.com/en/sites/CX_1/job/{item.get('Id')}",
                posted_date=convert_to_common_format(item.get("PostedDate", "")),
                experience_years=json.dumps(analysis["experience_years"]),
                skills=json.dumps(analysis["skills"]),
            )
            job_list.append(job)
        return job_list
