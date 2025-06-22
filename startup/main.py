import os
import sys
import json
from pathlib import Path

from startup.research_agent import StartupResearcher


def main():
    search_term = input("Enter the company name or search term: ").strip()

    # Set results directory the same as the script directory
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        results_dir.mkdir(parents=True)

    researcher = StartupResearcher(results_dir=results_dir)
    results = researcher.run(search_term)

    print(f"Reports: {results['reports']}")
    for paragraph in results["summaries"]:
        print(f"Summary: {paragraph}")

    print(f"Tags: {results['tags']}")
    print(f"Info: {results['info']}")

    print(f"Writing results to results directory: {results_dir}...")

    with (results_dir / (search_term + "-summaries.md")).open("w") as f:
        for paragraph in results["summaries"]:
            f.write(paragraph)
            f.write("\n\n")

    with (results_dir / (search_term + "-final_report.json")).open("w") as f:
        json.dump(results, f, indent=4)

    with (results_dir / (search_term + "-final_report.md")).open("w") as f:
        f.write(results["reports"])


if __name__ == "__main__":
    main()
