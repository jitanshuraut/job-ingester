from app.scrapers.B_Company.Blackrock import BlackrockScraper

if __name__ == "__main__":
    listener = BlackrockScraper()
    jobs = listener.fetch_jobs()
    print(jobs)