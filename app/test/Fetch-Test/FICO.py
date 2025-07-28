from app.scrapers.F_Company.FICO import FICOScraper

if __name__ == "__main__":
    listener = FICOScraper()
    jobs = listener.fetch_jobs()
    print(jobs)