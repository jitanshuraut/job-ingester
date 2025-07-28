from app.scrapers.A_Company.Akamai import AkamaiScraper

if __name__ == "__main__":
    listener = AkamaiScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)