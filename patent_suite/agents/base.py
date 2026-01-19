from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the patent_suite.
    Ensures a consistent interface for execution and tool access.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier for the agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief summary of the agent's purpose."""
        pass

    @abstractmethod
    def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main execution method for the agent.
        :param task: The specific instruction or task to perform.
        :param context: A dictionary containing relevant state (e.g., disclosure, session_id).
        :return: A dictionary containing the agent's output and metadata.
        """
        pass

    @abstractmethod
    def get_tools(self) -> List[Any]:
        """
        Returns the list of tools/functions this agent is authorized to use.
        """
        pass

if __name__ == "__main__":
    # Example of a concrete implementation
    class MockAgent(BaseAgent):
        @property
        def name(self): return "Mock"
        @property
        def description(self): return "A mock agent for testing."
        def run(self, task, context): return {"status": "ok", "task": task}
        def get_tools(self): return []

    agent = MockAgent()
    print(f"Agent: {agent.name} - {agent.description}")
    print(agent.run("test task", {}))
