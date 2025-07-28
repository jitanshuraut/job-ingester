from app.scrapers.A_Company.Amadeus_labs import AmadeusScraper

if __name__ == "__main__":
    listener = AmadeusScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)