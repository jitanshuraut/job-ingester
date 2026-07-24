from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class TeraDataScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, start: int) -> dict:
        url = "https://careers.teradata.com/graphql"
        payload = {
            "operationName": "searchJobs",
            "variables": {
                "hasPositionTitle": False, "hasEmploymentType": False,
                "hasJobCategory": False, "hasClassificationType": False,
                "hasGradeLevel": False, "hasRecruiter": False, "hasHiringManager": False,
                "hasUserDefined1": False, "hasUserDefined2": False, "hasUserDefined3": False,
                "hasUserDefined4": False, "hasUserDefined5": False, "hasUserDefined6": False,
                "hasUserDefined7": False, "hasUserDefined8": False, "hasUserDefined10": False,
                "hasUserDefined18": False, "hasUserDefinedBit1": False,
                "hasUserDefinedDecimal1": False, "hasUserDefinedDecimal2": False,
                "hasUserDefinedDecimal3": False, "hasUserDefinedDecimal4": False,
                "hasUserDefinedDecimal5": False, "hasUserDefinedDecimal6": False,
                "hasUserDefinedDecimal7": False, "hasUserDefinedDecimal50": False,
                "hasUserDefinedDecimal51": False, "hasUserDefinedLargeText1": False,
                "hasUserDefinedLargeText2": False, "hasUserDefinedLargeText3": False,
                "hasUserDefinedLargeText4": False, "hasUserDefinedLargeText5": False,
                "query": "", "first": self.PAGE_SIZE, "start": start,
                "filters": {"location": [], "workplaceType": [],
                            "jobCategory": ["3"], "positionType": [],
                            "sinceDatePosted": "WITHIN_LAST_WEEK"}
            },
            "extensions": {"trustedDocument": {"id": "search-jobs"}}
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://careers.teradata.com',
            'Referer': 'https://careers.teradata.com/jobs',
            'apollo-require-preflight': 'true',
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(response.status_code)
        return response.json()

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        results = first.get("data", {}).get("searchJobs", {}).get("results", {})
        all_nodes = list(results.get("nodes", []))
        has_next = results.get("pageInfo", {}).get("hasNextPage", False)
        start = self.PAGE_SIZE
        while has_next:
            try:
                data = self._fetch_page(start)
                r = data.get("data", {}).get("searchJobs", {}).get("results", {})
                all_nodes.extend(r.get("nodes", []))
                has_next = r.get("pageInfo", {}).get("hasNextPage", False)
                start += self.PAGE_SIZE
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed to fetch start={start}")
                break
        return self._parse_nodes(all_nodes)

    def parse(self, data) -> list[Job]:
        nodes = (data.get("data", {}).get("searchJobs", {})
                 .get("results", {}).get("nodes", []))
        return self._parse_nodes(nodes)

    def _parse_nodes(self, nodes: list) -> list[Job]:
        job_list = []
        for item in nodes:
            loc = item.get("primaryPlace") or {}
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id", ""),
                company="TeraData",
                location=loc.get("name", ""),
                url=f"https://careers.teradata.com/jobs/{item.get('number', '')}" if item.get("number") else "",
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
