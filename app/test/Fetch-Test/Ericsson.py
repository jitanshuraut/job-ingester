from app.scrapers.E_Company.Ericsson import EricssonScraper

if __name__ == "__main__":
    listener = EricssonScraper()
    jobs = listener.fetch_jobs()
    print(jobs)