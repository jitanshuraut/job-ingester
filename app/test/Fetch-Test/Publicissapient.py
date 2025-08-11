from app.scrapers.P_Company.Publicissapient import PublicissapientScraper

if __name__ == "__main__":
    listener = PublicissapientScraper()
    jobs = listener.fetch_jobs()
    print(jobs)