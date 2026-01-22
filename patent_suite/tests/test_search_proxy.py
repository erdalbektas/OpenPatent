import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.searcher import SearcherAgent

class TestSearcherAgentHybrid(unittest.TestCase):
    def setUp(self):
        self.mock_local_tool = MagicMock(return_value=[{"id": "L1", "title": "Local 1", "abstract": "abc"}])
        self.agent = SearcherAgent(search_tool=self.mock_local_tool)

    def test_run_local_search(self):
        # Ensure API key is NOT set
        if "OPENPATENT_API_KEY" in os.environ:
            del os.environ["OPENPATENT_API_KEY"]
            
        result = self.agent.run("holographic bread cutting", {})
        
        self.assertEqual(result["mode"], "free")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "L1")
        self.mock_local_tool.assert_called_once()

    @patch('requests.post')
    def test_run_remote_search_premium(self, mock_post):
        # Setup API key
        os.environ["OPENPATENT_API_KEY"] = "op-premium-key"
        
        # Setup mock remote response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "R1", "title": "Remote Premium", "abstract": "xyz"}]
        mock_post.return_value = mock_response

        result = self.agent.run("holographic bread cutting", {})

        self.assertEqual(result["mode"], "premium")
        self.assertEqual(result["results"][0]["id"], "R1")
        
        # Verify remote call
        mock_post.assert_called_once_with(
            "https://api.openpatent.com/search",
            json={"query": "holographic bread cutting"},
            headers={"Authorization": "Bearer op-premium-key"},
            timeout=30
        )

if __name__ == "__main__":
    unittest.main()
