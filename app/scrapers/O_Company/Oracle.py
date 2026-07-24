import math
import requests
from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class OracleScraper(BaseScraper):
    BASE_URL = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    LIMIT = 14

    HEADERS = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Connection": "keep-alive",
        "Content-Type": "application/vnd.oracle.adf.resourceitem+json;charset=utf-8",
        "Ora-Irc-Cx-UserId": "8a236611-3a6a-4566-b323-91791bab6c0a",
        "Ora-Irc-Language": "en",
        "Origin": "https://careers.oracle.com",
        "Referer": "https://careers.oracle.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }

    PARAMS = {
        "onlyData": "true",
        "expand": "requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields",
    }

    def _fetch_page(self, offset: int) -> dict:
        finder = (
            f"findReqs;siteNumber=CX_45001,"
            f"facetsList=LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS,"
            f"limit={self.LIMIT},offset={offset},"
            f'keyword="software",'
            f"locationId=300000000106947,"
            f"sortBy=RELEVANCY"
        )
        try:
            r = requests.get(
                self.BASE_URL,
                params={**self.PARAMS, "finder": finder},
                headers=self.HEADERS,
                timeout=30,
            )
            return r.json()
        except Exception:
            return {}

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        items = first.get("items")
        if not items:
            return []
        total = items[0].get("TotalJobsCount", 0)
        total_pages = math.ceil(total / self.LIMIT) if total else 1
        all_jobs = self.parse(first)
        for page in range(1, total_pages):
            data = self._fetch_page(page * self.LIMIT)
            all_jobs.extend(self.parse(data))
        return all_jobs

    def parse(self, data) -> list[Job]:
        items = data.get("items")
        if not items:
            return []
        req_list = items[0].get("requisitionList", [])
        jobs = []
        for item in req_list:
            title = item.get("Title", "")
            job_id = str(item.get("Id", ""))
            location = item.get("PrimaryLocation") or ""
            posted = item.get("PostedDate", "")
            url = f"https://careers.oracle.com/en/sites/jobsearch/job/{job_id}"
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Oracle",
                location=location,
                url=url,
                posted_date=convert_to_common_format(posted),
            ))
        return jobs



