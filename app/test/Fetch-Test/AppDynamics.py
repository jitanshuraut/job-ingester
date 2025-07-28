from app.scrapers.A_Company.App_Dynamics import AppDynamicsScraper

if __name__ == "__main__":
    listener = AppDynamicsScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)