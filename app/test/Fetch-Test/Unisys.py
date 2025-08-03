from app.scrapers.U_Company.Unisys import UnisysScraper

if __name__ == "__main__":
    listener = UnisysScraper()
    jobs = listener.fetch_jobs()
    print(jobs)