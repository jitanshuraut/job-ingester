from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json

class AsporaScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
        payload = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {"organizationHostedJobsPageName": "Aspora"},
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
        board = data.get("data", {}).get("jobBoard", {})
        teams = board.get("teams", [])
        team_map = {t["name"].lower(): t["id"] for t in teams}
        eng_id = team_map.get("engineering")
        if not eng_id:
            return []

        all_jobs = board.get("jobPostings", [])
        if not isinstance(all_jobs, list):
            return []

        job_list = []
        for item in all_jobs:
            if item.get("teamId") != eng_id:
                continue
            job_list.append(Job(
                title=item.get("title", ""),
                jobid=item.get("id", ""),
                company="Aspora",
                location="",
                url=f"https://jobs.ashbyhq.com/Aspora/{item.get('id', '')}",
                posted_date="",
            ))
        return job_list
