from app.scrapers.T_Company.TowerResearch import TowerResearchScraper

if __name__ == "__main__":
    listener = TowerResearchScraper()
    jobs = listener.fetch_jobs()
    print(jobs)