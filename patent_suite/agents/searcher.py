import os
import requests
from typing import Dict, List, Any
from .base import BaseAgent

class SearcherAgent(BaseAgent):
    """
    Expert in boolean logic and classification codes (CPC/IPC).
    Role: Senior Search Specialist.
    If premium: Uses OpenPatent Deep Search for superior indexing.
    If free: Uses standard mock search tool (Google Patents simulation).
    """
    def __init__(self, search_tool=None):
        # search_tool is the local fallback (e.g. Google Patents)
        self.local_search_tool = search_tool

    @property
    def name(self) -> str:
        return "Searcher"

    @property
    def description(self) -> str:
        return "Senior Search Specialist for prior art identification."

    def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes search. Routes to OpenPatent Cloud if API key is present.
        """
        disclosure = context.get("disclosure", task)
        api_key = os.getenv("OPENPATENT_API_KEY")

        if api_key:
            print(f"SearcherAgent: [Premium] Routing to Deep Search Proxy...")
            return self._run_remote_search(disclosure, api_key)
        else:
            print(f"SearcherAgent: [Free] Using local search tool (Google Patents)...")
            return self._run_local_search(disclosure)

    def _run_remote_search(self, query: str, api_key: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                "https://api.openpatent.com/search",
                json={"query": query},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
            response.raise_for_status()
            return {
                "status": "success",
                "mode": "premium",
                "results": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Deep Search failed: {str(e)}"
            }

    def _run_local_search(self, disclosure: str) -> Dict[str, Any]:
        # Mocking keyword extraction
        terms = disclosure.lower().split()
        main_subject = terms[0] if terms else "apparatus"
        keywords = f"({main_subject} AND toasting) OR (laser AND precision AND heating)"
        
        if self.local_search_tool:
            results = self.local_search_tool(keywords)
        else:
            # Inline fallback mock results
            results = [
                {"id": "US-1234567-A", "title": "Laser Toaster", "abstract": "A toaster using lasers."},
                {"id": "EP-9876543-B1", "title": "Precision Bread Heating", "abstract": "Methods for heating bread."}
            ]
        
        return {
            "status": "success",
            "mode": "free",
            "query": keywords,
            "results": results
        }

    def get_tools(self) -> List[Any]:
        return []
