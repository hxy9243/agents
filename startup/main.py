import os
import sys
import json
from pathlib import Path

from startup.research_agent import StartupResearcher


def main():
    search_term = input("Enter the company name or search term: ").strip()

    researcher = StartupResearcher()
    results = researcher.run(search_term)

    print(f"Reports: {results['reports']}")
    for paragraph in results["summaries"]:
        print(f"Summary: {paragraph}")

    print(f"Tags: {results['tags']}")
    print(f"Info: {results['info']}")

    with (Path("results") / (search_term + "-summaries.md")).open("w") as f:
        for paragraph in results["summaries"]:
            f.write(paragraph)
            f.write("\n\n")

    with (Path("results") / (search_term + "-final_report.json")).open("w") as f:
        json.dump(results, f, indent=4)

    with (Path("results") / (search_term + "-final_report.md")).open("w") as f:
        f.write(results["reports"])


if __name__ == "__main__":
    main()
