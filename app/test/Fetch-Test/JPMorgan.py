from app.scrapers.J_Company.JPMorgan import JPMorganScraper

if __name__ == "__main__":
    listener = JPMorganScraper()
    jobs = listener.fetch_jobs()
    print(jobs)