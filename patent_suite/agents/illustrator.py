import os
import requests
from typing import Dict, List, Any
from .base import BaseAgent

class IllustratorAgent(BaseAgent):
    """
    Expert in technical patent drawings and DALL-E 3 visual prompt engineering.
    Role: Professional Patent Illustrator.
    """
    
    @property
    def name(self) -> str:
        return "Illustrator"

    @property
    def description(self) -> str:
        return "Professional Patent Illustrator specializing in DALL-E 3 technical schematics."

    def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends the patent claims to the OpenPatent server to generate a technical illustration.
        """
        claims_text = context.get("claims_text", task)
        # We assume the user has configured the server URL and API key
        # For simplicity, we use the environment variables
        server_url = os.getenv("OPENPATENT_SERVER_URL", "http://0.0.0.0:8000")
        api_key = os.getenv("OPENPATENT_API_KEY")

        if not api_key:
            return {
                "status": "error",
                "message": "Premium Feature: OPENPATENT_API_KEY is required for automated illustration."
            }

        try:
            response = requests.post(
                f"{server_url}/api/v1/agents/illustrator/run",
                json={"claims_text": claims_text},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Illustration service failed: {str(e)}"
            }

    def get_tools(self) -> List[Any]:
        return []
