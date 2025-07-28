# app/scrapers/base.py
from typing import List
from app.models.job import Job

class BaseScraper:
    def fetch_jobs(self) -> List[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def fetch_raw(self):
        raise NotImplementedError("Subclasses must implement API call")

    def parse(self, raw_data) -> List[Job]:
        raise NotImplementedError("Subclasses must parse raw data to Job list")
