import json
import re

import requests
from bs4 import BeautifulSoup

from app.models.job import Job
from app.scrapers.base import BaseScraper
from app.utils.DateConverter import convert_to_common_format


class GEVernovaScraper(BaseScraper):
    BASE_URL = "https://careers.gevernova.com/jobs"
    FILTER_PARAMS = {
        "filter[country][0]": "India",
        "filter[cf_job_family][0]": "Applications and Embedded Software (Firmware); LPB",
        "filter[cf_job_family][1]": "Applications and Embedded Software (Firmware); PB",
        "filter[cf_job_family][2]": "Applications and Embedded Software (Firmware); SPB",
        "filter[cf_job_family][3]": "Applications and Software; LPB",
        "filter[cf_job_family][4]": "Applications and Software; PB",
        "filter[cf_job_family][5]": "Applications and Software; SPB",
        "filter[cf_job_family][6]": "Software Services; LPB",
        "filter[cf_job_family][7]": "Software Services; PB",
        "filter[cf_job_family][8]": "Sourcing_Sourcing; LPB",
    }

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def _fetch_page(self, page: int) -> str:
        url = f"{self.BASE_URL}/page/{page}" if page > 1 else self.BASE_URL
        r = self._session.get(url, params=self.FILTER_PARAMS, timeout=30)
        return r.text

    def _extract_from_state(self, html: str) -> list[Job]:
        m = re.search(r"window\.__PRELOAD_STATE__\s*=\s*(\{.+?\});", html, re.DOTALL)
        if not m:
            return []
        data = json.loads(m.group(1))
        jobs_data = data.get("jobSearch", {}).get("jobs", [])
        jobs = []
        for j in jobs_data:
            locs = j.get("locations", [])
            city_state = locs[0].get("cityState", "") if locs else ""
            posted = ""
            for cf in j.get("customFields", []):
                if cf.get("cfKey") == "cf_posting_start_date" and cf.get("value"):
                    posted = convert_to_common_format(cf["value"])
                    break
            req_id = j.get("requisitionID", "")
            title = j.get("title", "")
            if not title:
                continue
            jobs.append(Job(
                title=title,
                jobid=req_id,
                company="GEVernova",
                location=city_state,
                url=j.get("applyURL", ""),
                posted_date=posted,
            ))
        return jobs

    @staticmethod
    def _clean_location(raw: str) -> str:
        parts = raw.replace("Job Location", "").strip().split(",")
        if len(parts) >= 2:
            return f"{parts[0].strip()}, {parts[-1].strip()}"
        return raw

    def _parse_html(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "lxml")
        items = soup.select("li.results-list__item")
        jobs = []
        for item in items:
            a = item.select_one("h3.results-list__item-title a")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            loc_el = item.select_one("span.results-list__item-street--label")
            raw_loc = loc_el.get_text(strip=True) if loc_el else ""
            if "India" not in raw_loc and " IN " not in f" {raw_loc} ":
                continue
            location = self._clean_location(raw_loc)
            req_id = ""
            if href and "/job/" in href:
                req_id = href.rsplit("/", 1)[-1]
            date_els = item.select("[class*=custom2]")
            posted = ""
            if date_els:
                posted = convert_to_common_format(date_els[0].get_text(strip=True))
            jobs.append(Job(
                title=title,
                jobid=req_id,
                company="GEVernova",
                location=location,
                url=f"https://careers.gevernova.com{href}" if href.startswith("/") else href,
                posted_date=posted,
            ))
        return jobs

    def fetch_raw(self):
        return self._fetch_page(1)

    def fetch_jobs(self) -> list[Job]:
        first_html = self._fetch_page(1)
        state_jobs = self._extract_from_state(first_html)
        state_total = 0
        m = re.search(r"window\.__PRELOAD_STATE__\s*=\s*(\{.+?\});", first_html, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            state_total = data.get("jobSearch", {}).get("totalJob", 0)

        if state_jobs and state_total > 0:
            all_jobs = list(state_jobs)
            for page in range(2, (state_total // 10) + 2):
                html = self._fetch_page(page)
                page_jobs = self._parse_html(html)
                if not page_jobs:
                    break
                all_jobs.extend(page_jobs)
            return all_jobs
        return self._parse_html(first_html)

    def parse(self, html: str) -> list[Job]:
        return self._parse_html(html)
