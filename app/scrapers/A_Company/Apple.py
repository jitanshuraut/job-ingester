from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
import re


class AppleScraper(BaseScraper):
    def fetch_jobs(self) -> list[Job]:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        })

        search_page = "https://jobs.apple.com/en-in/search"
        try:
            r = session.get(search_page, timeout=30)
            print(".", end="", flush=True)
            html = r.text
        except requests.RequestException:
            return []

        csrf_match = re.search(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', html)
        csrf_token = csrf_match.group(1) if csrf_match else ""

        all_jobs = []
        page = 1
        while True:
            payload = {
                "query": "software",
                "filters": {"locations": ["postLocation-INDC"]},
                "page": page,
                "locale": "en-in",
                "sort": "relevance",
                "format": {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"},
            }
            try:
                r = session.post(
                    "https://jobs.apple.com/api/v1/search",
                    json=payload,
                    headers={
                        'accept': '*/*',
                        'browserlocale': 'en-in',
                        'content-type': 'application/json',
                        'locale': 'en_UK',
                        'origin': 'https://jobs.apple.com',
                        'referer': search_page,
                        'x-apple-csrf-token': csrf_token,
                    },
                    timeout=30,
                )
                print(".", end="", flush=True)
                data = r.json()
            except (requests.RequestException, json.JSONDecodeError):
                break

            results = data.get("res", {}).get("searchResults", [])
            total = data.get("res", {}).get("totalResults", 0)
            all_jobs.extend(results)

            if page * 10 >= total:
                break
            page += 1

        print()
        job_list = []
        for item in all_jobs:
            locs = item.get("locations") or []
            location = locs[0].get("name", "") if locs else ""
            job_list.append(Job(
                title=item.get("postingTitle", ""),
                jobid=item.get("reqId"),
                company="Apple",
                location=location,
                url=f"https://jobs.apple.com/en-in/details/{item.get('reqId', '')}",
                posted_date=item.get("postingDate", ""),
            ))
        return job_list
