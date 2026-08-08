#!/usr/bin/env python3
import sys
import json
from app.analyzer.categorizer import get_example_urls
from app.analyzer.main import analyze_jobs


def cmd_categories():
    examples = get_example_urls(limit_per_platform=3)
    print(f"{'PLATFORM':25s} {'COUNT':>6s}  EXAMPLES")
    print("-" * 100)
    for platform in sorted(examples.keys()):
        urls = examples[platform]
        print(f"{platform:25s} {len(urls):>6d}")
        for company, url in urls:
            print(f"  {company:20s} {url}")
        print()


def cmd_analyze(company=None, limit=None, save=False):
    results = analyze_jobs(company=company, limit=limit, save=save)
    print(f"\nTotal analyzed: {len(results)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze_jobs.py categories              - show URL category examples")
        print("  python analyze_jobs.py analyze [company] [limit] [--save]")
        sys.exit(1)

    if sys.argv[1] == "categories":
        cmd_categories()
    elif sys.argv[1] == "analyze":
        company = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
        limit = None
        save = False
        for arg in sys.argv[2:]:
            if arg.startswith("--limit="):
                limit = int(arg.split("=")[1])
            elif arg == "--save":
                save = True
        if company and company.isdigit():
            limit = int(company)
            company = None
        cmd_analyze(company=company, limit=limit, save=save)
    else:
        print(f"Unknown command: {sys.argv[1]}")
