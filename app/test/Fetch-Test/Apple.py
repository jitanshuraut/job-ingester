from app.scrapers.A_Company.Apple import AppleScraper

if __name__ == "__main__":
    listener = AppleScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)