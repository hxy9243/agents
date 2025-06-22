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

from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path

from dotenv import load_dotenv
import dspy
from dspy import Signature, Module

from exa_py import Exa

import logging

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)

load_dotenv()


lm = dspy.LM(model="gemini/gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY"))


dspy.configure(lm=lm, track_usage=False)


exa = Exa(api_key=os.environ.get("EXA_API_KEY"))


def exa_search(search, num_results: int = 5) -> List[str]:
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
    """The search agent queries the search term and returns the search terms for the search engine, including:

    - Funding
    - Leadership
    - Product or Service Details
    - Customers
    - Latest News
    - Other information if available
    """

    search_term: str = dspy.InputField(
        desc="The company name or the URL link mentioning the company"
    )

    company_name: str = dspy.OutputField(desc="The company name")
    company_url: str = dspy.OutputField(desc="The URL of the company")
    summary: str = dspy.OutputField(desc="A short summary of the company")
    search_terms: List[str] = dspy.OutputField(
        desc=(
            "List of the search terms for the search engine to research more about the company, "
            "including funding, leadership, product and service details, customers, etc."
        )
    )


class SearchAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ReAct(
            signature=SearchAgentSignature,
            tools=[exa_search],
        )
        self.search_results = {}

    def forward(self, search_term: str) -> Dict[str, Dict]:
        logger.info(f"Running search agent with search term: {search_term}")

        pred = self.lm(search_term=search_term)

        with open("history.txt", "w") as f:
            f.write("{}".format(self.lm.history))

        return pred


class InfoExtractAgentSignature(Signature):
    """The information extraction agent cleans up the raw text from the URL, generates a report, and extract useful information from the result.
    It should keep most of the text instead of a short summary.

    It's critical that each paragraph should include the URL as a markdown link, and the text should be in markdown format, so that each
    statement can be referenced back to the original source URL fullpath.
    """

    topic: str = dspy.InputField(
        desc="The topic of the company, e.g., Overview, Investors, Funding, Product, Customers, Competitors"
    )
    search_results: Dict[str, Dict] = dspy.InputField(
        desc="The search results from the search agent, from URL to the report text"
    )

    text: str = dspy.OutputField(
        desc="The cleaned up version of the raw text from URL scrape"
    )
    tags: Optional[List[str]] = dspy.OutputField(
        desc="The tags and categorization of the company based on the search results",
        default=[],
    )
    info: Optional[Dict[str, str]] = dspy.OutputField(
        desc="The detailed information about the company, including investors, funding, product, funding, customers, competitors, etc",
        default={},
    )


class InfoExtractAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ChainOfThought(signature=InfoExtractAgentSignature)

    def forward(self, topic: str, search_results: Dict[str, str]) -> Dict[str, str]:
        logger.info(f"Running info extract agent with search term: {search_results}")

        return self.lm(topic=topic, search_results=search_results)


class RewriteAgentSignature(Signature):
    """The rewrite agent rearranges the input text in markdown format to make it more readable, without losing details or changing its meaning.
    It should try to keep the most important information and rewrite for conciseness, and NOT to just summarize.

    The rewrite result should include the URLs in the text as markdown links, as references for the information provided.
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
        logger.info(f"Running rewrite agent: {input_text[:200]}")

        return self.lm(input_text=input_text, extracted_info=extracted_info)


class FinalReportAgentSignature(Signature):
    """The report agent generates a final report in markdown format based on each paragraph and extracted info.
    It should include the section title and content, rearrange the paragraphs if necessary for readability.
    Do not include backquotes or code blocks in the report, as it should be a readable markdown report.

    It should generate a final report that best reflect the search results and content, for example:

    - Overview: a summary of the company, including its mission, vision, and values
    - Product: very detailed explanation of the company's products, including their features, user experience, and benefits.
        It should be as much detailed as possible.
    - Investors: a list of the company's investors, with their names and links to their profiles
    - Funding: a list of the company's funding history, including the amount raised and the investors involved
    - Customers: a detailed breakdown of the company's customers, including their names and links to their profiles
    - Competitors: a summary of the company's competitors, including their names and links to their profiles

    The rewrite result should keep the URLs in the text as markdown links, as references for the information provided.
    If there are multiple URLs referenced, they should be listed separately.
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


class FinalReportAgent(Module):
    def __init__(self):
        super().__init__()

        self.lm = dspy.ChainOfThought(
            signature=FinalReportAgentSignature,
        )

    def forward(
        self, paragraphs: Dict[str, str], extracted_info: Dict[str, str]
    ) -> str:
        return self.lm(paragraphs=paragraphs, extracted_info=extracted_info)


class StartupResearcher:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.info_extract_agent = InfoExtractAgent()
        self.rewrite_agent = RewriteAgent()
        self.report_agent = FinalReportAgent()

    def _load_results(self, path: str):
        with open(path, "r") as f:
            return json.load(f)

    def _save_results(self, search_results, path: str):
        with open(path, "w") as f:
            json.dump(search_results, f, indent=4)

    def initial_search(self, search_term: str) -> Dict[str, str]:
        """Search for the company and return the search results,
        with topic as the key and the list of results as the value."""

        pred = self.search_agent(search_term=search_term)

        return {
            "company_name": pred.company_name,
            "company_url": pred.company_url,
            "summary": pred.summary,
            "search_terms": pred.search_terms,
        }

    def further_search(self, initial_results: Dict[str, str]) -> List[str]:
        search_terms = initial_results["search_terms"]

        company_name = pred.company_name.replace(" ", "_").replace("/", "_")
        cache_path = Path("results") / (company_name + ".search.json")

        results = dict()

        if Path(cache_path).exists():
            logger.info(f"Loading existing results from {cache_path}...")
            results = self._load_results(cache_path)
        else:
            for term in pred.search_terms:
                logger.info(f"searching for {term}...")
                result = exa_search(search=term, num_results=5)
                results[term] = result

            self._save_results(results, cache_path)

        return results

    def run(self, search_term: str) -> Dict[str, Any]:
        """Run the company research process and return the final report."""
        initial_results = self.initial_search(search_term)

        logger.info(
            f"Researching company name: {initial_results['company_name']} on {initial_results['company_url']}\n===="
        )
        logger.info(f"Summary: {initial_results['summary']}\n====")
        logger.info(
            f"To continue research, additional search terms could be: {initial_results['search_terms']}"
        )

        cont = input(
            "Do you want to continue with the search? (y/n): "
        ).strip().lower()
        if cont != "y" and cont != "yes":
            logger.info("Exiting the research process...")
            return {}

        results = self.further_search(initial_results)
        texts = dict()
        tags = set()
        extracted_info = dict()

        logger.info(f"Search results: {results}")

        # extract information from each topic
        for topic, search_results in results.items():
            extract_agent = InfoExtractAgent()
            extract_results = extract_agent(topic=topic, search_results=search_results)

            texts[topic] = extract_results.text
            tags.update(extract_results.tags)
            extracted_info[topic] = extract_results.info

        logger.info("Search results: " + json.dumps(texts, indent=2))
        logger.info("Extracted info: " + json.dumps(extracted_info, indent=2))
        logger.info(f"Tags: {tags}")

        # clean up and rewrite the paragraphs
        rewritten_results = []
        for topic, text in texts.items():
            logger.info(f"Topic: {topic}\nReport: {text}\n")

            rewrite_agent = RewriteAgent()
            rewritten_results.append(
                rewrite_agent(
                    input_text=text,
                    extracted_info=extracted_info[topic],
                ).rewritten_results
            )

        # generate the final report
        report = self.report_agent(
            paragraphs=rewritten_results,
            extracted_info=extracted_info,
        )

        return {
            "reports": report.report,
            "summaries": rewritten_results,
            "tags": list(tags),
            "info": extracted_info,
        }
