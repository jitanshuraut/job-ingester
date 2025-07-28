from app.scrapers.C_Company.Cashfree import CashfreeScraper

if __name__ == "__main__":
    listener = CashfreeScraper()
    jobs = listener.fetch_jobs()
    print(jobs)