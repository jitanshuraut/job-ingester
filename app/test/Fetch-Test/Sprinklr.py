from app.scrapers.S_Company.Sprinklr import SprinklrScraper

if __name__ == "__main__":
    listener = SprinklrScraper()
    jobs = listener.fetch_jobs()
    print(jobs)