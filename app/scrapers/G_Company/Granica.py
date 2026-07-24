from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json

class GranicaScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
        payload = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {"organizationHostedJobsPageName": "granica"},
            "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { teams { id name } jobPostings { id title teamId } } }",
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def parse(self, data) -> list[Job]:
        jobs_data = data.get("data", {}).get("jobBoard", {}).get("jobPostings", [])
        if not isinstance(jobs_data, list):
            return []
        teams = {t.get("id"): t.get("name", "") for t in data.get("data", {}).get("jobBoard", {}).get("teams", [])}
        job_list = []
        for item in jobs_data:
            team_name = teams.get(item.get("teamId", ""), "")
            location = ""
            title = item.get("title", "")
            parts = title.split(" - ")
            if len(parts) > 1:
                location = parts[-1]
            job = Job(
                title=title,
                jobid=item.get("id", ""),
                company="Granica",
                location=location,
                url=f"https://jobs.ashbyhq.com/granica/{item.get('id', '')}",
                posted_date="",
            )
            job_list.append(job)
        return job_list
