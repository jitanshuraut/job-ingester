from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
import urllib.parse


class MSCI_Scraper(BaseScraper):
    HITS_PER_PAGE = 50

    def fetch_raw(self):
        url = "https://rvmob42dfh-dsn.algolia.net/1/indexes/*/queries"
        params = {
            "x-algolia-agent": "Algolia for JavaScript (4.23.3)",
            "x-algolia-api-key": "629e647c6a9a8b542fb1022001313a7e",
            "x-algolia-application-id": "RVMOB42DFH",
        }
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://careers.msci.com",
            "Referer": "https://careers.msci.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        filter_arr = [[
            "town_city_country:Bengaluru | India",
            "town_city_country:Coimbatore | India",
            "town_city_country:Mumbai | India",
            "town_city_country:Pune | India",
        ]]
        query_params = (
            f"facetFilters={urllib.parse.quote(json.dumps(filter_arr))}"
            f"&hitsPerPage={self.HITS_PER_PAGE}&page=0&query="
        )
        payload = {"requests": [{"indexName": "production__mscicare2201__sort-rank", "params": query_params}]}
        try:
            r = requests.post(url, params=params, json=payload, headers=headers, timeout=30)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            return {}

    def parse(self, data) -> list[Job]:
        results = data.get("results", [{}])
        hits = results[0].get("hits", []) if results else []
        job_list = []
        for item in hits:
            title = item.get("title", "")
            if not title:
                continue
            city = item.get("location", "") or item.get("town_city", "") or item.get("locality", "")
            country = item.get("country", "")
            location = f"{city}, {country}" if city and country else city or country
            req_id = item.get("ats_requisition_id", "")
            url_slug = item.get("jd_url", "")
            job_url = f"https://careers.msci.com{url_slug}" if url_slug else ""
            job_list.append(Job(
                title=title,
                jobid=req_id,
                company="MSCI",
                location=location,
                url=job_url,
                posted_date="",
            ))
        return job_list
