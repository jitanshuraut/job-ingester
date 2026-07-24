from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class GoldManScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, page_number: int) -> dict:
        url = "https://api-higher.gs.com/gateway/api/v1/graphql"
        payload = {
            "operationName": "GetRoles",
            "variables": {
                "searchQueryInput": {
                    "page": {"pageSize": self.PAGE_SIZE, "pageNumber": page_number},
                    "sort": {"sortStrategy": "RELEVANCE", "sortOrder": "DESC"},
                    "filters": [
                        {"filterCategoryType": "EXPERIENCE_LEVEL", "filters": [{"filter": "Associate", "subFilters": []}]},
                        {"filterCategoryType": "JOB_FUNCTION", "filters": [{"filter": "Software Engineering", "subFilters": []}]},
                        {"filterCategoryType": "LOCATION", "filters": [{"filter": "India", "subFilters": [{"filter": "Karnataka", "subFilters": [{"filter": "Bengaluru", "subFilters": []}]}, {"filter": "Maharashtra", "subFilters": [{"filter": "Mumbai", "subFilters": []}]}, {"filter": "Telangana", "subFilters": [{"filter": "Hyderabad", "subFilters": []}]}]}]}
                    ],
                    "experiences": ["PROFESSIONAL", "EARLY_CAREER"],
                    "searchTerm": "",
                }
            },
            "query": """query GetRoles($searchQueryInput: RoleSearchQueryInput!) {
  roleSearch(searchQueryInput: $searchQueryInput) {
    totalCount
    items {
      roleId
      corporateTitle
      jobTitle
      jobFunction
      locations {
        primary
        state
        country
        city
        __typename
      }
      status
      division
      skills
      jobType {
        code
        description
        __typename
      }
      lastPostedDate
      externalSource {
        sourceId
        __typename
      }
      __typename
    }
    __typename
  }
}""",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'api-higher.gs.com',
            'Origin': 'api-higher.gs.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        role_search = first.get("data", {}).get("roleSearch", {})
        total_count = role_search.get("totalCount", 0)
        all_items = list(role_search.get("items", []))
        for page_num in range(1, -(-total_count // self.PAGE_SIZE)):
            data = self._fetch_page(page_num)
            all_items.extend(data.get("data", {}).get("roleSearch", {}).get("items", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("data", {}).get("roleSearch", {}).get("items", []))

    @staticmethod
    def _format_date(instant_str: str) -> str:
        if not instant_str:
            return ""
        return convert_to_common_format(instant_str[:10])

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            locations = item.get("locations") or []
            loc_str = ", ".join(f"{l.get('city','')}, {l.get('state','')}" for l in locations if l.get('city'))
            job = Job(
                title=item.get("jobTitle", ""),
                jobid=item.get("roleId"),
                company="GoldMan",
                location=loc_str,
                url="",
                posted_date=self._format_date(item.get("lastPostedDate", "")),
            )
            job_list.append(job)
        return job_list
