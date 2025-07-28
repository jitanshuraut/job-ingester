from app.scrapers.B_Company.BNY import BNYScraper

if __name__ == "__main__":
    listener = BNYScraper()
    jobs = listener.fetch_jobs()
    print(jobs)