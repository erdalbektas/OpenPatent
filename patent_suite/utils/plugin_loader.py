import os
import importlib.util
import inspect
from typing import Dict, Type
from patent_suite.agents.base import BaseAgent

class AgentRegistry:
    """
    A centralized registry for all discovered agents.
    """
    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        """Registers an agent class."""
        name = agent_class.__name__
        if name not in cls._agents:
            print(f"AgentRegistry: Registered {name}")
            cls._agents[name] = agent_class

    @classmethod
    def get_agent(cls, name: str) -> Type[BaseAgent]:
        """Retrieves an agent class by name."""
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """Lists all registered agents and their descriptions."""
        return {name: cls._get_desc(cls._agents[name]) for name in cls._agents}
    
    @staticmethod
    def _get_desc(agent_class):
        # We instantiate a temp instance to get the description if it's not a static property
        # For simplicity in this mock, we assume it's accessible or we look at docstring
        return agent_class.__doc__.split('\n')[0].strip() if agent_class.__doc__ else "No description"

class PluginLoader:
    """
    Scans a directory for custom agents and registers them in the AgentRegistry.
    """
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)

    def discover_plugins(self):
        """
        Scans for .py files and loads BaseAgent subclasses.
        """
        print(f"PluginLoader: Scanning {self.plugin_dir} for custom agents...")
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                file_path = os.path.join(self.plugin_dir, filename)
                module_name = filename[:-3]
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Inspect the module for BaseAgent subclasses
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                                AgentRegistry.register(obj)
                                
                except Exception as e:
                    print(f"PluginLoader: Error loading plugin {filename}: {e}")

if __name__ == "__main__":
    # Test with a mock directory
    loader = PluginLoader("custom_agents")
    loader.discover_plugins()
    print("Registered Agents:", AgentRegistry.list_agents())
