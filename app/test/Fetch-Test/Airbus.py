from app.scrapers.A_Company.Airbus import AirbusScraper

if __name__ == "__main__":
    listener = AirbusScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)