# app/scrapers/base.py
from typing import List, Optional
from app.models.job import Job

class BaseScraper:
    proxy: Optional[str] = None

    def fetch_jobs(self) -> List[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def fetch_raw(self):
        raise NotImplementedError("Subclasses must implement API call")

    def parse(self, raw_data) -> List[Job]:
        raise NotImplementedError("Subclasses must parse raw data to Job list")
