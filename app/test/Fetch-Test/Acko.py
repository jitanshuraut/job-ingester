from app.scrapers.A_Company.Acko import AckoScraper

if __name__ == "__main__":
    listener = AckoScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)