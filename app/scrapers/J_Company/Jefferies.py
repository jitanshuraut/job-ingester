from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests

API = "https://hdid.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"

HEADERS = {
    "accept": "*/*",
    "origin": "https://careers.jefferies.com",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36",
}

LOCATIONS = {
    "india": "300000000361484",
    "pune": "300000547982107",
    "new york": "300000010173138",
    "london": "300000268117789",
    "tokyo": "300000268117678",
    "hong kong": "300000000361454",
}

CATEGORIES = {
    "it": "300000009105524",
    "information technology": "300000009105524",
    "investment banking": "300000009105557",
    "research": "300000009105569",
    "risk management": "300000009105542",
    "sales/trading": "300000009105551",
    "operations": "300000009105539",
    "controllers/finance": "300000009105509",
    "administrative": "300000009105506",
    "compliance": "300000009105503",
    "wealth management": "300000009105566",
}


def _build_finder(limit=100, offset=0, location_id=None, category_id=None):
    params = {
        "siteNumber": "CX_1",
        "facetsList": "LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS",
        "limit": limit,
        "offset": offset,
        "sortBy": "RELEVANCY",
    }
    if location_id:
        params["locationId"] = location_id
    if category_id:
        params["selectedCategoriesFacet"] = category_id
    parts = ",".join(f"{k}={v}" for k, v in params.items())
    return f"findReqs;{parts}"


class JefferiesScraper(BaseScraper):
    def __init__(self):
        self.location_id = LOCATIONS["india"]
        self.category_id = CATEGORIES["it"]

    def fetch_raw(self):
        all_jobs = []
        offset, limit, total = 0, 100, None
        while True:
            params = {
                "onlyData": "true",
                "expand": "requisitionList.workLocation",
                "finder": _build_finder(limit=limit, offset=offset, location_id=self.location_id, category_id=self.category_id),
            }
            resp = requests.get(API, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            item = data["items"][0]
            if total is None:
                total = item.get("TotalJobsCount", 0)
            reqs = item.get("requisitionList", [])
            all_jobs.extend(reqs)
            if len(reqs) < limit:
                break
            offset += limit
        return all_jobs

    def parse(self, raw) -> list[Job]:
        jobs = []
        for r in raw:
            wl = r.get("workLocation", [{}])[0]
            jobs.append(Job(
                title=r["Title"],
                jobid=str(r["Id"]),
                company="Jefferies",
                location=r.get("PrimaryLocation", ""),
                url=f"https://careers.jefferies.com/jefferies/job/jefferies-{r['Id']}-Senior-Professional/job/",
                posted_date=convert_to_common_format(r.get("PostedDate", "")) or "",
            ))
        return jobs