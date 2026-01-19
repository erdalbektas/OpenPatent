import os
import sys

# Setup path to include patent_suite
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from patent_suite.utils import index_mpep, search_mpep

class MPEPRag:
    """
    RAG tool interface for MPEP sections.
    Uses centralized logic in utils.py.
    """
    def scrape_and_index(self):
        return index_mpep()

    def search(self, query, top_k=2):
        return search_mpep(query, top_k)

if __name__ == "__main__":
    rag = MPEPRag()
    rag.scrape_and_index()
    res = rag.search("eligibility")
    print(f"Search results for 'eligibility': {res}")
