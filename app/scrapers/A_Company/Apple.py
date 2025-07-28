from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json



class AppleScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.apple.com/api/v1/searc"

        params = {"query": "", "filters": {"locations": ["postLocation-INDC"], "teams": [{"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-AF"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-CLD"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-COS"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-DSR"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-EPM"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-ISTECH"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-MCHLN"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-SEC"}, {
            "team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-SQAT"}, {"team": "teamsAndSubTeams-SFTWR", "subTeam": "subTeam-WSFT"}, {"team": "teamsAndSubTeams-MLAI", "subTeam": "subTeam-MLI"}, {"team": "teamsAndSubTeams-MLAI", "subTeam": "subTeam-DLRL"}, {"team": "teamsAndSubTeams-MLAI", "subTeam": "subTeam-NLP"}, {"team": "teamsAndSubTeams-MLAI", "subTeam": "subTeam-CV"}, {"team": "teamsAndSubTeams-MLAI", "subTeam": "subTeam-AR"}]}, "page": 1, "locale": "en-us", "sort": "", "format": {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"}}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'jobs.apple.com',
            'Origin': 'jobs.apple.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=30)
            json_data = response.json()
            print(response.status_code)
            return json_data
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print("Response text:")
            print(
                response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("res", {}).get("searchResults", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("postingTitle", ""),
                jobid=item.get("reqId"),
                company="Apple",
                location=item.get("location", ""),
                url=item.get("absolute_url", ""),
                posted_date=item.get("postingDate", "")
            )
            job_list.append(job)
        return job_list


if __name__ == "__main__":
    listener = AppleScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)
