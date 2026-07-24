from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class PayUScraper(BaseScraper):
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    def fetch_raw(self):
        url = "https://careers.payu.in/PayU/go/_/514880/"
        params = {"q": "", "q2": "", "alertId": "", "facility": "", "title": "software", "location": "", "date": ""}
        try:
            response = self._session.get(url, params=params, timeout=30)
            print(response.status_code)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            print(f"Request failed")
            return ""

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, html: str) -> list[Job]:
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("tr.data-row")
        job_list = []
        for row in rows:
            cells = row.select("td")
            if len(cells) < 4:
                continue
            req_id = cells[0].get_text(strip=True)
            title_link = cells[1].select_one("a")
            if not title_link:
                continue
            title = title_link.get_text(strip=True)
            href = title_link.get("href", "")
            location = cells[2].get_text(strip=True)
            date_str = cells[3].get_text(strip=True)
            full_url = f"https://careers.payu.in{href}" if href else ""
            job = Job(
                title=title,
                jobid=req_id,
                company="PayU",
                location=location,
                url=full_url,
                posted_date=convert_to_common_format(date_str),
            )
            job_list.append(job)
        return job_list
