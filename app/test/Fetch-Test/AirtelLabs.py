from app.scrapers.A_Company.Airtel_labs import AirtelLabsScraper

if __name__ == "__main__":
    listener = AirtelLabsScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)