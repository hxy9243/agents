"""
The company research agent is designed specifically for gathering
a company's information.

It breaks the process into the following agents:

- Research and info gathering:
  - Exa: search and crawl API
- Data mining: summarize each piece of research results and data extraction,
  clean up and summarize the raw data
- Analysis:
  - Analyze and provide insight on each aspect of the company
  - Generate tags and categorization of the company
- Summary: summarize and generate the final report
"""

from typing import List, Dict, Any
import os
import sys
from urllib.parse import urlparse
import json
from pathlib import Path
import logging
from urllib.parse import urlparse

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import dspy
from dspy import Signature, Module, Tool
from exa_py import Exa


load_dotenv()

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


lm = dspy.LM(
    api_base=os.getenv("LM_BASE_URL"),
    api_key=os.getenv("LM_API_KEY"),
    model="openai/Llama-4-Maverick-17B-128E-Instruct",
)
dspy.configure(lm=lm, track_usage=False)


exa = Exa(api_key=os.environ.get("EXA_API_KEY"))


def search(search, num_results: int = 5) -> List[str]:
    resp = exa.search_and_contents(
        search,
        text=True,
        num_results=num_results,
    )
    return [
        {
            "search_term": search,
            "url": r.url,
            "title": r.title,
            "text": r.text,
        }
        for r in resp.results
    ]


class SearchAgentSignature(Signature):
    """The search agent queries the search term and returns the search terms for the search engine."""

    search_term: str = dspy.InputField(
        desc="The company name or the URL link mentioning the company"
    )

    company_name: str = dspy.OutputField(desc="The company name")
    company_url: str = dspy.OutputField(desc="The URL of the company")
    search_terms: List[str] = dspy.OutputField(
        desc=(
            "List of the search terms for the search engine to research more about the company, "
            "including investors, product, funding, customers, competitors, etc"
        )
    )


class SearchAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ReAct(
            signature=SearchAgentSignature,
            tools=[search],
        )
        self.search_results = {}

    def forward(self, search_term: str) -> Dict[str, Dict]:
        pred = self.lm(search_term=search_term)

        with open("history.txt", "w") as f:
            f.write("{}".format(self.lm.history))

        return pred


class InfoExtractAgentSignature(Signature):
    """The information extraction agent cleans up the raw text from the URL, generates a report, and extract useful information from the result.
    It should keep most of the text instead of a short summary.
    """

    topic: str = dspy.InputField(
        desc="The topic of the company, e.g., Overview, Investors, Funding, Product, Customers, Competitors"
    )
    search_results: Dict[str, Dict] = dspy.InputField(
        desc="The search results from the search agent"
    )

    text: str = dspy.OutputField(
        desc="The cleaned up version of the raw text from URL scrape"
    )
    tags: List[str] = dspy.OutputField(
        desc="The tags and categorization of the company based on the search results"
    )
    info: Dict[str, str] = dspy.OutputField(
        desc="The detailed information about the company, including investors, funding, product, funding, customers, competitors, etc"
    )


class InfoExtractAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ChainOfThought(signature=InfoExtractAgentSignature)

    def forward(self, topic: str, search_results: Dict[str, str]) -> Dict[str, str]:
        return self.lm(topic=topic, search_results=search_results)


class RewriteAgentSignature(Signature):
    """The rewrite agent rearranges the input text in markdown format to make it more readable, without losing details or changing its meaning.
    It should try to keep the most important information and rewrite for conciseness, and NOT to just summarize.

    The rewrite result should include the URLs in the text as markdown links, as references for the information provided.

    The rewritten results should be as informative as possible, and should include tables and/or list for readability as much as possible at the end.
    """

    input_text: Dict[str, str] = dspy.InputField(
        desc="The search results from the search agent, mapping from URL to the report text"
    )
    extracted_info: Dict[str, str] = dspy.InputField(
        desc="The detailed information about the company, including overview, investors, funding, product, funding, customers, competitors, etc"
    )

    rewritten_results: str = dspy.OutputField(
        desc="The rewritten results in text, in markdown format, with URLs as references"
    )


class RewriteAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ChainOfThought(
            signature=RewriteAgentSignature,
        )

    def forward(
        self, input_text: Dict[str, str], extracted_info: Dict[str, str]
    ) -> Dict[str, str]:
        return self.lm(input_text=input_text, extracted_info=extracted_info)


class ReportAgentSignature(Signature):
    """The report agent generates a final report in markdown format based on each paragraph and extracted info.
    It should include the section title and content, rearrange the paragraphs if necessary for readability.

    It should generate a final report that best reflect the search results and content, for example:

    - Overview: a summary of the company, including its mission, vision, and values
    - Product: very detailed explanation of the company's products, including their features and benefits
    - Investors: a list of the company's investors, with their names and links to their profiles
    - Funding: a list of the company's funding history, including the amount raised and the investors involved
    - Customers: a detailed breakdown of the company's customers, including their names and links to their profiles
    - Competitors: a summary of the company's competitors, including their names and links to their profiles

    The rewrite result should keep the URLs in the text as markdown links, as references for the information provided.
    """

    paragraphs: List[str] = dspy.InputField(
        desc="The list of paragraphs inputs, each paragraph is a summary of the search results for a specific topic"
    )
    extracted_info: Dict[str, str] = dspy.InputField(
        desc="The information extracted from each specific topic"
    )
    report: str = dspy.OutputField(
        desc="The final report of the company research, with section title and content, in markdown format"
    )


class ReportAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ChainOfThought(
            signature=ReportAgentSignature,
        )

    def forward(
        self, paragraphs: Dict[str, str], extracted_info: Dict[str, str]
    ) -> str:
        return self.lm(paragraphs=paragraphs, extracted_info=extracted_info)


class CompanyResearcher:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.info_extract_agent = InfoExtractAgent()
        self.rewrite_agent = RewriteAgent()
        self.report_agent = ReportAgent()

    def _load_results(self, path: str):
        with open(path, "r") as f:
            return json.load(f)

    def _save_results(self, search_results, path: str):
        with open(path, "w") as f:
            json.dump(search_results, f, indent=4)

    def search(self, search_term: str) -> Dict[str, List]:
        """Search for the company and return the search results, with topic as the key and the list of results as the value."""

        pred = self.search_agent(search_term=search_term)

        logging.info(
            f"researching company name: {pred.company_name} on {pred.company_url}\n===="
        )
        logging.info(
            f"To continue research, additional search terms could be: {pred.search_terms}"
        )

        company_name = pred.company_name.replace(" ", "_").replace("/", "_")
        cache_path = Path("results") / (company_name + ".search.json")

        results = dict()

        if Path(cache_path).exists():
            logging.info(f"loading existing results from {cache_path}...")
            results = self._load_results(cache_path)
        else:
            for term in pred.search_terms:
                logging.info(f"searching for {term}...")
                result = search(search=term, num_results=5)
                results[term] = result

            self._save_results(results, cache_path)

        return results

    def run(self, search_term: str) -> Dict[str, Any]:
        """Run the company research process and return the final report."""
        results = self.search(search_term)

        texts = dict()
        tags = set()
        extracted_info = dict()

        logging.info(f"Search results: {results}")

        # extract information from each topic
        for topic, search_results in results.items():
            extract_agent = InfoExtractAgent()
            extract_results = extract_agent(topic=topic, search_results=search_results)

            texts[topic] = extract_results.text
            tags.update(extract_results.tags)
            extracted_info.update(extract_results.info)

        logging.info("Search results:", json.dumps(texts, indent=2))
        logging.info("Extracted info:", json.dumps(extracted_info, indent=2))
        logging.info("Tags:", list(tags))

        # clean up and rewrite the paragraphs
        rewritten_results = []
        for topic, text in texts.items():
            logging.info(f"Topic: {topic}\nReport: {text}\n")

            rewrite_agent = RewriteAgent()
            rewritten_results.append(
                rewrite_agent(input_text=text, extracted_info=extracted_info)
            )

        # generate the final report
        report = self.report_agent(
            paragraphs=rewritten_results,
            extracted_info=extracted_info,
        )

        return {
            "reports": report.report,
            "tags": list(tags),
            "info": extracted_info,
        }


def main():
    researcher = CompanyResearcher()

    search_term = "vapi"
    results = researcher.run(search_term)

    print(f"Reports: {results['reports']}")
    print(f"Tags: {results['tags']}")
    print(f"Info: {results['info']}")


main()
