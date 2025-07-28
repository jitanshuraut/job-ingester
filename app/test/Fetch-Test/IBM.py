from app.scrapers.I_Company.IBM import IBMScraper

if __name__ == "__main__":
    listener = IBMScraper()
    jobs = listener.fetch_jobs()
    print(jobs)