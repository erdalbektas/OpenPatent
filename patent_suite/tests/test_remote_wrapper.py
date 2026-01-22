import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.remote_wrapper import RemoteAgent

class TestRemoteAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RemoteAgent()
        os.environ["OPENPATENT_API_KEY"] = "test-api-key"

    @patch('requests.post')
    def test_run_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success", "data": "analysis result"}
        mock_post.return_value = mock_response

        # Execute
        result = self.agent.run("analyze claims", {"claims": "1. A device..."})

        # Verify
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["data"], "analysis result")
        
        # Verify call arguments
        mock_post.assert_called_once_with(
            "https://api.openpatent.com/agents/run",
            json={"claims": "1. A device...", "task": "analyze claims"},
            headers={
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json"
            },
            timeout=30
        )

    def test_missing_api_key(self):
        # Remove API key from env
        if "OPENPATENT_API_KEY" in os.environ:
            del os.environ["OPENPATENT_API_KEY"]
            
        with self.assertRaises(PermissionError) as cm:
            self.agent.run("test", {})
        
        self.assertIn("Premium Feature", str(cm.exception))

    @patch('requests.post')
    def test_run_error(self, mock_post):
        # Setup mock for connection error
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection Failed")

        # Execute
        result = self.agent.run("test", {})

        # Verify
        self.assertEqual(result["status"], "error")
        self.assertIn("Connection Failed", result["message"])

if __name__ == "__main__":
    unittest.main()
