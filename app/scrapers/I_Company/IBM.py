from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class IBMScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://www-api.ibm.com/search/api/v2"

        payload = {"appId": "careers", "scopes": ["careers2"], "query": {"bool": {"must": []}}, "post_filter": {"bool": {"must": [{"term": {"field_keyword_08": "Software Engineering"}}, {"term": {"field_keyword_18": "Entry Level"}}, {"term": {"field_keyword_05": "India"}}]}}, "aggs": {"field_keyword_172": {"filter": {"bool": {"must": [{"term": {"field_keyword_08": "Software Engineering"}}, {"term": {"field_keyword_18": "Entry Level"}}, {"term": {"field_keyword_05": "India"}}]}}, "aggs": {"field_keyword_17": {"terms": {"field": "field_keyword_17", "size": 6}}, "field_keyword_17_count": {"cardinality": {"field": "field_keyword_17"}}}}, "field_keyword_083": {"filter": {"bool": {"must": [{"term": {"field_keyword_18": "Entry Level"}}, {"term": {"field_keyword_05": "India"}}]}}, "aggs": {"field_keyword_08": {"terms": {"field": "field_keyword_08", "size": 6}}, "field_keyword_08_count": {"cardinality": {"field": "field_keyword_08"}}}}, "field_keyword_184": {
            "filter": {"bool": {"must": [{"term": {"field_keyword_08": "Software Engineering"}}, {"term": {"field_keyword_05": "India"}}]}}, "aggs": {"field_keyword_18": {"terms": {"field": "field_keyword_18", "size": 6}}, "field_keyword_18_count": {"cardinality": {"field": "field_keyword_18"}}}}, "field_keyword_055": {"filter": {"bool": {"must": [{"term": {"field_keyword_08": "Software Engineering"}}, {"term": {"field_keyword_18": "Entry Level"}}]}}, "aggs": {"field_keyword_05": {"terms": {"field": "field_keyword_05", "size": 1000}}, "field_keyword_05_count": {"cardinality": {"field": "field_keyword_05"}}}}}, "size": 50, "sort": [{"dcdate": "desc"}, {"_score": "desc"}], "lang": "zz", "localeSelector": {}, "sm": {"query": "", "lang": "zz"}, "_source": ["_id", "title", "url", "description", "language", "entitled", "field_keyword_17", "field_keyword_08", "field_keyword_18", "field_keyword_19"]}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'www-api.ibm.com',
            'Origin': 'www-api.ibm.com',
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
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("hits",{}).get("hits",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("_source").get("title", ""),
                jobid=item.get("Id"),
                company="IBM",
                location=item.get("_source").get("field_keyword_19", ""),
                url=item.get("_source").get("url", ""),
                posted_date=convert_to_common_format(item.get("published", "")),
            )
            job_list.append(job)
        return job_list
