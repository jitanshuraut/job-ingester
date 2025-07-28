from app.scrapers.A_Company.American_express import AmericanExpressScraper

if __name__ == "__main__":
    listener = AmericanExpressScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)