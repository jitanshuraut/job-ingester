from dataclasses import dataclass


@dataclass
class Job:
    title: str
    jobid: str
    company: str
    location: str
    url: str
    posted_date: str
