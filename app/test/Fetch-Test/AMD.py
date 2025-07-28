from app.scrapers.A_Company.AMD import AMDScraper

if __name__ == "__main__":
    listener = AMDScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)