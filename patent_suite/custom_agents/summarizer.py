from patent_suite.agents.base import BaseAgent
from typing import Dict, List, Any

class PriorArtSummarizer(BaseAgent):
    """
    Custom agent that specializes in summarizing dense prior art documents.
    """
    @property
    def name(self) -> str:
        return "PriorArtSummarizer"

    @property
    def description(self) -> str:
        return "Expert in distilling complex technical patents into 3-bullet summaries."

    def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "summary": "This is a custom summary of the prior art."
        }

    def get_tools(self) -> List[Any]:
        return []
