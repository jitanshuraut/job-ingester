from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class AkamaiScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_1,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,lastSelectedFacet=TITLES,selectedLocationsFacet=300000000469285,selectedTitlesFacet=ENG,sortBy=POSTING_DATES_DESC"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://jobs.akamai.com',
            'Origin': 'https://jobs.akamai.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url,headers=headers,timeout=30)
            json_data = response.json()
            print(response.status_code)
            return json_data
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        items = data.get("items", [])
        first_job=[]
        if items:
            requisition_list = items[0].get("requisitionList", [])
            if requisition_list:
                first_job = requisition_list
            else:
                print("No jobs found in requisitionList.")
        else:
            print("No items found in data.")
        job_list = []
        for item in first_job:
            job = Job(
                title=item.get("Title", ""),
                jobid=item.get("Id"),
                company="AirtelLabs",
                location=item.get("workLocation")[0].get("TownOrCity",""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("PostedDate", "")),
            )
            job_list.append(job)
        return job_list

