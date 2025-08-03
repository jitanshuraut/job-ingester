from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class TexasScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://edbz.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,lastSelectedFacet=CATEGORIES,locationId=300000000361484,selectedCategoriesFacet=300000068853972,sortBy=POSTING_DATES_DESC"

        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'edbz.fa.us2.oraclecloud.com',
            'Origin': 'edbz.fa.us2.oraclecloud.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.get(
                url, headers=headers, timeout=30)
            print(response.status_code)
            json_data = response.json()
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
        items = data.get("items",[])[0].get("requisitionList", [])
        job_list = []
        for item in items:
            job = Job(
                title=item.get("Title", ""),
                jobid=item.get("id"),
                company="Texas",
                location=item.get("PrimaryLocation", ""),
                url=item.get("canonicalPositionUrl", ""),
                posted_date=convert_to_common_format(
                    item.get("PostedDate", "")),
            )
            job_list.append(job)
        return job_list
