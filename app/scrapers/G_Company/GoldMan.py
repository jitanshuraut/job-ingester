from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class GoldManScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://api-higher.gs.com/gateway/api/v1/graphql"

        payload = {"operationName":"GetRoles","variables":{"searchQueryInput":{"page":{"pageSize":20,"pageNumber":0},"sort":{"sortStrategy":"RELEVANCE","sortOrder":"DESC"},"filters":[{"filterCategoryType":"EXPERIENCE_LEVEL","filters":[{"filter":"Associate","subFilters":[]}]},{"filterCategoryType":"JOB_FUNCTION","filters":[{"filter":"Software Engineering","subFilters":[]}]},{"filterCategoryType":"LOCATION","filters":[{"filter":"India","subFilters":[{"filter":"Karnataka","subFilters":[{"filter":"Bengaluru","subFilters":[]}]},{"filter":"Maharashtra","subFilters":[{"filter":"Mumbai","subFilters":[]}]},{"filter":"Telangana","subFilters":[{"filter":"Hyderabad","subFilters":[]}]}]}]}],"experiences":["PROFESSIONAL","EARLY_CAREER"],"searchTerm":""}},"query":"query GetRoles($searchQueryInput: RoleSearchQueryInput!) {\n  roleSearch(searchQueryInput: $searchQueryInput) {\n    totalCount\n    items {\n      roleId\n      corporateTitle\n      jobTitle\n      jobFunction\n      locations {\n        primary\n        state\n        country\n        city\n        __typename\n      }\n      status\n      division\n      skills\n      jobType {\n        code\n        description\n        __typename\n      }\n      externalSource {\n        sourceId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"}

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
        job_posts = data.get("data",{}).get("roleSearch",{}).get("items",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("jobTitle", ""),
                jobid=item.get("roleId"),
                company="GoldMan",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
