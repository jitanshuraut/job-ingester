from app.scrapers.C_Company.CrowdStrike import CrowdStrikeScraper

if __name__ == "__main__":
    listener = CrowdStrikeScraper()
    jobs = listener.fetch_jobs()
    print(jobs)