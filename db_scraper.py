#!/usr/bin/env python3
"""Deutsche Bank India tech jobs scraper.

Fetches from the public beesite API, no auth needed.

Usage:
    python3 db_scraper.py                          # India tech jobs
    python3 db_scraper.py --country 81             # India (default)
    python3 db_scraper.py --division 10052         # Technology (default)
    python3 db_scraper.py --keyword Engineer       # filter title
    python3 db_scraper.py --json                   # JSON output
    python3 db_scraper.py --all                    # all jobs, no division/country filter
"""

import argparse
import json
import re
import sys
from datetime import datetime

import requests

BASE_URL = "https://api-deutschebank.beesite.de/search/"


def build_query(division=None, country=None):
    criteria = []
    if division:
        criteria.append({"CriterionName": "UserArea.ProDivision", "CriterionValue": division})
    if country:
        criteria.append({"CriterionName": "PositionLocation.Country", "CriterionValue": country})

    return {
        "LanguageCode": "en",
        "SearchParameters": {
            "FirstItem": 1,
            "CountItem": 50,
            "MatchedObjectDescriptor": [
                "Facet:ProfessionCategory",
                "Facet:UserArea.ProDivision",
                "Facet:Profession",
                "Facet:PositionLocation.CountrySubDivision",
                "Facet:PositionOfferingType.Code",
                "Facet:PositionSchedule.Code",
                "Facet:PositionLocation.City",
                "Facet:PositionLocation.Country",
                "Facet:JobCategory.Code",
                "Facet:CareerLevel.Code",
                "Facet:PositionHiringYear",
                "Facet:PositionFormattedDescription.Content",
                "PositionID", "PositionTitle", "PositionURI",
                "ScoreThreshold", "OrganizationName",
                "PositionFormattedDescription.Content",
                "PositionLocation.CountryName",
                "PositionLocation.CountrySubDivisionName",
                "PositionLocation.CityName",
                "PositionLocation.Longitude", "PositionLocation.Latitude",
                "PositionIndustry.Name", "JobCategory.Name",
                "CareerLevel.Name", "PositionSchedule.Name",
                "PositionOfferingType.Name", "PublicationStartDate",
                "UserArea.GradEduInstCountry", "PositionImport",
                "PositionHiringYear", "PositionID",
            ],
            "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}],
        },
        "SearchCriteria": criteria,
    }


def scrape(division=10052, country=81):
    query = build_query(division, country)
    params = {"data": json.dumps(query, separators=(",", ":"))}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://careers.db.com",
        "Referer": "https://careers.db.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36",
    }
    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    sr = data.get("SearchResult", {})
    items = sr.get("SearchResultItems", [])
    total = sr.get("SearchResultCountAll", len(items))
    return items, total


def print_jobs(items, total):
    if not items:
        print("No jobs found.")
        return

    print(f"\n{len(items)} jobs (of {total} total)\n")
    print(f"{'Date':12s} | {'Title':55s} | {'Location':25s}")
    print("-" * 95)
    for item in items:
        d = item.get("MatchedObjectDescriptor", {})
        title = d.get("PositionTitle", "N/A")
        locs = d.get("PositionLocation", [])
        loc = locs[0].get("CityName", "") if locs else ""
        loc += ", " + locs[0].get("CountryName", "") if locs else ""
        pub = d.get("PublicationChannel", [{}])[0].get("StartDate", "") if d.get("PublicationChannel") else ""
        if pub and len(pub) >= 10:
            pub = pub[:10]
        print(f"{pub:12s} | {title[:55]:55s} | {loc[:25]:25s}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deutsche Bank jobs scraper")
    parser.add_argument("--division", type=int, default=10052, help="ProDivision code (default: 10052 = Technology)")
    parser.add_argument("--country", type=int, default=81, help="Country code (default: 81 = India)")
    parser.add_argument("--keyword", help="Filter by keyword in title")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--all", action="store_true", help="No division/country filters")
    args = parser.parse_args()

    division = None if args.all else args.division
    country = None if args.all else args.country

    items, total = scrape(division=division, country=country)

    if args.keyword:
        kw = args.keyword.lower()
        items = [i for i in items if kw in i.get("MatchedObjectDescriptor", {}).get("PositionTitle", "").lower()]

    if args.json:
        print(json.dumps({"total": total, "matching": len(items), "jobs": items}, indent=2))
    else:
        print_jobs(items, total)
