from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class TeraDataScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://careers.teradata.com/graphql"

        payload = {"operationName": "searchJobs", "variables": {"hasPositionTitle": False, "hasEmploymentType": False, "hasJobCategory": False, "hasClassificationType": False, "hasGradeLevel": False, "hasRecruiter": False, "hasHiringManager": False, "hasUserDefined1": False, "hasUserDefined2": False, "hasUserDefined3": False, "hasUserDefined4": False, "hasUserDefined5": False, "hasUserDefined6": False, "hasUserDefined7": False, "hasUserDefined8": False, "hasUserDefined10": False, "hasUserDefined18": False, "hasUserDefinedBit1": False, "hasUserDefinedDecimal1": False, "hasUserDefinedDecimal2": False, "hasUserDefinedDecimal3": False, "hasUserDefinedDecimal4": False, "hasUserDefinedDecimal5": False, "hasUserDefinedDecimal6": False, "hasUserDefinedDecimal7": False, "hasUserDefinedDecimal50": False, "hasUserDefinedDecimal51": False, "hasUserDefinedLargeText1": False, "hasUserDefinedLargeText2": False, "hasUserDefinedLargeText3": False, "hasUserDefinedLargeText4": False, "hasUserDefinedLargeText5": False, "query": "", "first": 10, "start": 0, "filters": {"location": [], "workplaceType": [], "jobCategory": ["3"], "positionType": [], "sinceDatePosted": "WITHIN_LAST_WEEK"}},
                   "query": "query searchJobs($query: String, $start: Int, $first: Int, $after: String, $sort: [GoogleJobDiscoverySearchSort], $filters: GoogleJobDiscoverySearchFiltersInput, $hasPositionTitle: Boolean!, $hasEmploymentType: Boolean!, $hasJobCategory: Boolean!, $hasClassificationType: Boolean!, $hasGradeLevel: Boolean!, $hasRecruiter: Boolean!, $hasHiringManager: Boolean!, $hasUserDefined1: Boolean!, $hasUserDefined2: Boolean!, $hasUserDefined3: Boolean!, $hasUserDefined4: Boolean!, $hasUserDefined5: Boolean!, $hasUserDefined6: Boolean!, $hasUserDefined7: Boolean!, $hasUserDefined8: Boolean!, $hasUserDefined10: Boolean!, $hasUserDefined18: Boolean!, $hasUserDefinedBit1: Boolean!, $hasUserDefinedDecimal1: Boolean!, $hasUserDefinedDecimal2: Boolean!, $hasUserDefinedDecimal3: Boolean!, $hasUserDefinedDecimal4: Boolean!, $hasUserDefinedDecimal5: Boolean!, $hasUserDefinedDecimal6: Boolean!, $hasUserDefinedDecimal7: Boolean!, $hasUserDefinedDecimal50: Boolean!, $hasUserDefinedDecimal51: Boolean!, $hasUserDefinedLargeText1: Boolean!, $hasUserDefinedLargeText2: Boolean!, $hasUserDefinedLargeText3: Boolean!, $hasUserDefinedLargeText4: Boolean!, $hasUserDefinedLargeText5: Boolean!) {\n  searchJobs: searchGoogleJobDiscovery(query: $query, start: $start, first: $first, after: $after, sort: $sort, filters: $filters) {\n    __typename\n    results {\n      __typename\n      nodes {\n        ...jobPostingFields\n        __typename\n      }\n      pageInfo {\n        hasNextPage\n        hasPreviousPage\n        startCursor\n        endCursor\n        __typename\n      }\n      totalCount\n    }\n  }\n}\n\nfragment jobPostingFields on JobPosting {\n  __typename\n  id\n  key\n  number\n  status\n  title\n  descriptionHTML\n  workplaceType\n  viewerAppliedToJob\n  postType\n  structuredDataJSON\n  positionType {\n    __typename\n    id\n    name\n  }\n  primaryPlace {\n    __typename\n    id\n    name\n  }\n  places {\n    __typename\n    nodes {\n      __typename\n      name\n      id\n    }\n    pageInfo {\n      __typename\n      hasNextPage\n      hasPreviousPage\n      startCursor\n      endCursor\n    }\n  }\n  payTransparencyRequired\n  payRangeLow\n  payRangeMid\n  payRangeHigh\n  payRangeType\n  currencyCode\n  postedOn\n  applyOnExternalATS\n  hasATSLink\n  indeedApplyHtml\n  eeoText\n  positionTitle @include(if: $hasPositionTitle) {\n    __typename\n    id\n    name\n  }\n  classificationType @include(if: $hasClassificationType) {\n    __typename\n    id\n    name\n  }\n  jobCategory @include(if: $hasJobCategory) {\n    __typename\n    id\n    name\n  }\n  employmentType @include(if: $hasEmploymentType) {\n    __typename\n    id\n    name\n  }\n  gradeLevel @include(if: $hasGradeLevel) {\n    __typename\n    id\n    name\n  }\n  recruiter @include(if: $hasRecruiter) {\n    __typename\n    id\n    fullName\n  }\n  hiringManager @include(if: $hasHiringManager) {\n    __typename\n    id\n    fullName\n  }\n  userDefined1 @include(if: $hasUserDefined1) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined2 @include(if: $hasUserDefined2) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined3 @include(if: $hasUserDefined3) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined4 @include(if: $hasUserDefined4) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined5 @include(if: $hasUserDefined5) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined6 @include(if: $hasUserDefined6) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined7 @include(if: $hasUserDefined7) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined8 @include(if: $hasUserDefined8) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined10 @include(if: $hasUserDefined10) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefined18 @include(if: $hasUserDefined18) {\n    __typename\n    id\n    name\n    auxData1\n    auxData2\n  }\n  userDefinedBit1 @include(if: $hasUserDefinedBit1)\n  userDefinedDecimal1 @include(if: $hasUserDefinedDecimal1)\n  userDefinedDecimal2 @include(if: $hasUserDefinedDecimal2)\n  userDefinedDecimal3 @include(if: $hasUserDefinedDecimal3)\n  userDefinedDecimal4 @include(if: $hasUserDefinedDecimal4)\n  userDefinedDecimal5 @include(if: $hasUserDefinedDecimal5)\n  userDefinedDecimal6 @include(if: $hasUserDefinedDecimal6)\n  userDefinedDecimal7 @include(if: $hasUserDefinedDecimal7)\n  userDefinedDecimal50 @include(if: $hasUserDefinedDecimal50)\n  userDefinedDecimal51 @include(if: $hasUserDefinedDecimal51)\n  userDefinedLargeText1 @include(if: $hasUserDefinedLargeText1)\n  userDefinedLargeText2 @include(if: $hasUserDefinedLargeText2)\n  userDefinedLargeText3 @include(if: $hasUserDefinedLargeText3)\n  userDefinedLargeText4 @include(if: $hasUserDefinedLargeText4)\n  userDefinedLargeText5 @include(if: $hasUserDefinedLargeText5)\n}\n"}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'careers.teradata.com',
            'Origin': 'careers.teradata.com',
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
        job_posts = data.get("data", {}).get(
            "searchJobs", {}).get("results", {}).get("nodes", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id"),
                company="TeraData",
                location=item.get("location", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
