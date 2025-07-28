from app.scrapers.A_Company.Able import AbleScraper

if __name__ == "__main__":
    listener = AbleScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)