from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import re
import requests

CAREERS_PAGE = "https://cornerstone.csod.com/ats/careersite/search.aspx?c=cornerstone&country=in"
API_URL = "https://us-galaxy.api.csod.com/rec-job-search/external/jobs"


class CornerstoneScraper(BaseScraper):
    def fetch_raw(self):
        resp = requests.get(CAREERS_PAGE, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        m = re.search(r'"token":"([^"]+)"', resp.text)
        if not m:
            raise RuntimeError("Could not extract auth token from careers page")
        token = m.group(1)

        headers = {
            "content-type": "application/json",
            "origin": "https://cornerstone.csod.com",
            "referer": "https://cornerstone.csod.com/",
            "user-agent": "Mozilla/5.0",
            "authorization": f"Bearer {token}",
        }

        all_jobs = []
        page = 1
        page_size = 25
        total = None
        body_template = {
            "careerSiteId": 2,
            "careerSitePageId": 2,
            "pageNumber": page,
            "pageSize": page_size,
            "cultureId": 1,
            "searchText": "",
            "cultureName": "en-US",
            "states": [],
            "cities": [],
            "placeID": "",
            "radius": None,
            "postingsWithinDays": None,
            "customFieldCheckboxKeys": [],
            "customFieldDropdowns": [],
            "customFieldRadios": [],
            "countryCodes": ["in"],
        }

        while True:
            body = dict(body_template, pageNumber=page)
            resp = requests.post(API_URL, headers=headers, json=body, timeout=15)
            resp.raise_for_status()
            data = resp.json()["data"]
            if total is None:
                total = data["totalCount"]
            all_jobs.extend(data["requisitions"])
            if len(all_jobs) >= total or len(data["requisitions"]) < page_size:
                break
            page += 1
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for r in raw:
            locs = [l.get("city", "") for l in r.get("locations", [])]
            rid = r["requisitionId"]
            jobs.append(Job(
                title=r["displayJobTitle"],
                jobid=str(rid),
                company="Cornerstone",
                location=", ".join(locs),
                url=f"https://cornerstone.csod.com/ux/ats/careersite/2/home/requisition/{rid}?c=cornerstone",
                posted_date=convert_to_common_format(r.get("postingEffectiveDate", "")) or "",
            ))
        return jobs