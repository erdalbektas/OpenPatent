import os
import requests
from typing import Dict, List, Any
from .base import BaseAgent

class Config:
    @property
    def OPENPATENT_API_KEY(self):
        return os.getenv("OPENPATENT_API_KEY")

config = Config()

class RemoteAgent(BaseAgent):
    """
    An agent that looks like a local agent but acts as an API client
    to a remote agent execution service.
    """
    
    @property
    def name(self) -> str:
        return "RemoteAgent"

    @property
    def description(self) -> str:
        return "A wrapper for executing agents via the OpenPatent Cloud API."

    def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent remotely via the OpenPatent API.
        """
        if not config.OPENPATENT_API_KEY:
            raise PermissionError("Premium Feature: OPENPATENT_API_KEY is required for remote agent access.")
        
        # Merge task into context for the API payload
        payload = context.copy()
        payload["task"] = task
        
        try:
            response = requests.post(
                "https://api.openpatent.com/agents/run",
                json=payload,
                headers={
                    "Authorization": f"Bearer {config.OPENPATENT_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Remote agent execution failed: {str(e)}"
            }

    def get_tools(self) -> List[Any]:
        """
        Remote agents typically have their tools managed server-side.
        """
        return []

if __name__ == "__main__":
    # Internal test/usage example
    os.environ["OPENPATENT_API_KEY"] = "mock-key"
    agent = RemoteAgent()
    print(f"Running {agent.name}...")
    # This will fail with a real request if the key is invalid, 
    # but shows the interface works.
