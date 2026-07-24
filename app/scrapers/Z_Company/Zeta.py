import requests
from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class ZetaScraper(BaseScraper):
    URL = "https://api.lever.co/v0/postings/zeta?group=team&mode=json"
    HEADERS = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.zeta.tech",
        "Referer": "https://www.zeta.tech/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def fetch_jobs(self) -> list[Job]:
        try:
            r = requests.get(self.URL, headers=self.HEADERS, timeout=30)
            teams = r.json()
        except Exception:
            return []

        jobs = []
        for team in teams:
            for posting in team.get("postings") or []:
                if posting.get("country") != "IN":
                    continue
                title = posting.get("text") or ""
                job_id = posting.get("id") or ""
                location = (posting.get("categories") or {}).get("location") or ""
                url = posting.get("hostedUrl") or posting.get("applyUrl") or ""
                ts = posting.get("createdAt")
                jobs.append(Job(
                    title=title,
                    jobid=job_id,
                    company="Zeta",
                    location=location,
                    url=url,
                    posted_date=convert_to_common_format(ts / 1000 if ts else ""),
                ))
        return jobs



