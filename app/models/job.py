from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    title: str
    jobid: str
    company: str
    location: str
    url: str
    posted_date: str
    experience_years: str = ""
    skills: str = ""
