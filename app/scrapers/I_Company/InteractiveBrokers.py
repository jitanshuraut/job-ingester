from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import json


class InteractiveBrokersScraper(PlaywrightScraper):
    TIMEOUT = 60000

    def _get_csrf(self, page) -> str:
        cookies = page.context.cookies()
        for c in cookies:
            if "__Host-next-auth.csrf-token" in c.get("name", ""):
                raw = c["value"]
                return raw.split("%7C")[0] if "%7C" in raw else raw
        return ""

    def fetch_jobs(self):
        def callback(page):
            page.goto(
                "https://jobs.dayforcehcm.com/ibgllc/CANDIDATEPORTAL",
                wait_until="domcontentloaded",
                timeout=self.TIMEOUT,
            )
            page.wait_for_timeout(5000)
            csrf = self._get_csrf(page)
            if not csrf:
                return []

            all_jobs = []
            offset = 0
            while True:
                payload = {
                    "clientNamespace": "ibgllc",
                    "jobBoardCode": "CANDIDATEPORTAL",
                    "cultureCode": "en-US",
                    "searchText": "",
                    "locationString": "india",
                    "distance": 500,
                    "distanceUnit": 0,
                    "paginationStart": offset,
                }
                code = f"""
                async () => {{
                    const resp = await fetch('https://jobs.dayforcehcm.com/api/geo/ibgllc/jobposting/search', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json', 'x-csrf-token': '{csrf}'}},
                        body: JSON.stringify({json.dumps(payload)})
                    }});
                    return await resp.json();
                }}
                """
                try:
                    data = page.evaluate(code)
                except Exception:
                    break
                posts = data.get("jobPostings", [])
                if not posts:
                    break
                for item in posts:
                    loc = item.get("postingLocations", [{}])[0]
                    all_jobs.append(Job(
                        title=item.get("jobTitle", ""),
                        jobid=str(item.get("jobReqId", "")),
                        company="Interactive Brokers",
                        location=loc.get("formattedAddress", loc.get("cityName", "")),
                        url="https://jobs.dayforcehcm.com/ibgllc/CANDIDATEPORTAL",
                        posted_date=convert_to_common_format(item.get("postingStartTimestampUTC", "")),
                    ))
                max_count = data.get("maxCount", 0)
                offset += len(posts)
                if offset >= max_count:
                    break

            return all_jobs

        return self._run_playwright(callback)
