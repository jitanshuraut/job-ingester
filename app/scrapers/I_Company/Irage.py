from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup

class IrageScraper(BaseScraper):
    def fetch_raw(self):
        try:
            r = requests.get("https://irage.in/recruitment.php", headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            print(r.status_code)
            return r.text
        except requests.RequestException:
            print("Request failed")
            return ""

    def fetch_jobs(self) -> list[Job]:
        html = self.fetch_raw()
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all("a", href=lambda h: h and "job_descriptions.php?jd_id=" in h)
        seen = set()
        job_list = []
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if not text or text in ("Apply", "↳Apply") or href in seen:
                continue
            seen.add(href)
            jd_id = href.split("jd_id=")[-1]
            location = self._fetch_location(jd_id)
            job = Job(
                title=text,
                jobid=jd_id,
                company="iRage",
                location=location or "Mumbai, India",
                url=f"https://irage.in/{href}",
                posted_date="",
            )
            job_list.append(job)
        return job_list

    def _fetch_location(self, jd_id: str) -> str:
        try:
            r = requests.get(f"https://irage.in/job_descriptions.php?jd_id={jd_id}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            soup = BeautifulSoup(r.text, "lxml")
            text = soup.get_text()
            for line in text.split("\n"):
                line = line.strip()
                if line.lower().startswith("/ "):
                    return line[2:].strip()
                if "location" in line.lower() and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        return parts[1].strip()
        except requests.RequestException:
            pass
        return ""

    def parse(self, data) -> list[Job]:
        return self.fetch_jobs()
