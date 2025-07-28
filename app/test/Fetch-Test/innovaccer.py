from app.scrapers.I_Company.Innovaccer import InnovaccerScraper

if __name__ == "__main__":
    listener = InnovaccerScraper()
    jobs = listener.fetch_jobs()
    print(jobs)