from app.scrapers.B_Company.BrowserStack import BroswerStackScraper

if __name__ == "__main__":
    listener = BroswerStackScraper()
    jobs = listener.fetch_jobs()
    print(jobs)