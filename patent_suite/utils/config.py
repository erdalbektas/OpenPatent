import os

class ConfigManager:
    """
    Manages loading and aggregating system-wide and agent-specific rules.
    Loads from settings.yaml.
    """
    def __init__(self, config_path=None):
        if config_path is None:
            # Default to the root of the patent_suite directory
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings.yaml')
        
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """
        Loads the YAML config. Mocking YAML parsing for simplicity.
        """
        if not os.path.exists(self.config_path):
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return {}

        # Simple mock YAML parser (supports only the structure defined in Task 21)
        # In a real app, use: import yaml; return yaml.safe_load(f)
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            # Very basic mock parsing logic
            config = {"global_rules": "", "agent_rules": {}}
            
            sections = content.split('\n\n')
            for section in sections:
                if section.startswith("global_rules:"):
                    # Extract text after |
                    rules = section.split('|', 1)[1] if '|' in section else ""
                    config["global_rules"] = rules.strip()
                elif section.startswith("agent_rules:"):
                    # Extract agent blocks
                    agent_blocks = section.split('\n  ')
                    for i in range(1, len(agent_blocks)):
                        parts = agent_blocks[i].split(': |', 1)
                        if len(parts) == 2:
                            agent_name = parts[0].strip()
                            agent_rule = parts[1].strip()
                            config["agent_rules"][agent_name] = agent_rule

            return config
        except Exception as e:
            print(f"Error parsing config: {e}")
            return {}

    def get_agent_rules(self, agent_name):
        """
        Returns a concatenated string of global rules and agent-specific rules.
        """
        global_rules = self.config.get("global_rules", "")
        agent_rules = self.config.get("agent_rules", {}).get(agent_name, "")
        
        combined_rules = f"=== GLOBAL SYSTEM RULES ===\n{global_rules}\n\n"
        combined_rules += f"=== AGENT-SPECIFIC RULES ({agent_name}) ===\n{agent_rules}"
        
        return combined_rules

if __name__ == "__main__":
    manager = ConfigManager()
    print(manager.get_agent_rules("Drafter"))
