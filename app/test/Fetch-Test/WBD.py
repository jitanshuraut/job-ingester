from app.scrapers.W_Company.WBD import WBDScraper

if __name__ == "__main__":
    listener = WBDScraper()
    jobs = listener.fetch_jobs()
    print(jobs)