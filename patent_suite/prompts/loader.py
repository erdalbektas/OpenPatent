import os
from patent_suite.utils.config import ConfigManager

class PromptLoader:
    """
    Loads agent system prompts and enriches them with rules from ConfigManager.
    """
    def __init__(self, prompts_dir=None):
        if prompts_dir is None:
            # Default to the prompts directory relative to this file
            prompts_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.prompts_dir = prompts_dir
        self.config_manager = ConfigManager()

    def load_prompt(self, agent_name, base_filename=None, jurisdiction="USPTO"):
        """
        Loads the base prompt, appends agent rules, and injects jurisdictional constraints.
        """
        if base_filename is None:
            # Default to agent_name.txt lowercased
            base_filename = f"{agent_name.lower()}.txt"
        
        prompt_path = os.path.join(self.prompts_dir, base_filename)
        
        base_prompt = ""
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as f:
                base_prompt = f.read()
        else:
            print(f"Warning: Base prompt file {prompt_path} not found. Using empty string.")
            base_prompt = f"Role: {agent_name} Agent\n"

        # Fetch rules from ConfigManager
        rules = self.config_manager.get_agent_rules(agent_name)
        
        # Fetch jurisdictional rules
        jur_rules = self.config_manager.config.get("jurisdiction_rules", {}).get(jurisdiction, "")
        
        # Hydrate dynamic agent list if placeholder exists (for Orchestrator)
        if "{{AVAILABLE_AGENTS}}" in base_prompt:
            from patent_suite.utils.plugin_loader import AgentRegistry
            agents = AgentRegistry.list_agents()
            agent_list_str = "\n".join([f"- {name}: {desc}" for name, desc in agents.items()])
            base_prompt = base_prompt.replace("{{AVAILABLE_AGENTS}}", agent_list_str)

        # Construct final prompt with clear delimiter
        final_prompt = base_prompt
        final_prompt += f"\n\n### JURISDICTIONAL CONSTRAINTS ({jurisdiction}) (STRICT COMPLIANCE REQUIRED):\n"
        final_prompt += jur_rules
        final_prompt += "\n\n### USER DEFINED RULES (MUST FOLLOW):\n"
        final_prompt += rules
        
        return final_prompt

if __name__ == "__main__":
    loader = PromptLoader()
    # Test loading Orchestrator prompt
    full_prompt = loader.load_prompt("Orchestrator", "orchestrator.txt")
    print(full_prompt)
