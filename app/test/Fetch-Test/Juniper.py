from app.scrapers.J_Company.Juniper import JuniperScraper

if __name__ == "__main__":
    listener = JuniperScraper()
    jobs = listener.fetch_jobs()
    print(jobs)