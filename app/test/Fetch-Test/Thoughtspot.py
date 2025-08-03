from app.scrapers.T_Company.Thoughtspot import ThoughtspotScraper

if __name__ == "__main__":
    listener = ThoughtspotScraper()
    jobs = listener.fetch_jobs()
    print(jobs)