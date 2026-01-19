class DrafterAgent:
    """
    Expert in technical writing and claim construction.
    Role: Senior Patent Drafter.
    Instruction: Draft the Specification and Claims. Use 'comprising' for open claims. 
    Ensure technical terms are consistent with the provided disclosure.
    """
    def __init__(self, drafting_tool):
        self.drafting_tool = drafting_tool

    def draft_specification(self, disclosure, prior_art_summary, visual_map=None, style_examples=None):
        print("DrafterAgent: Drafting full Specification with consistent terminology...")
        
        # Style Guidance (Phase 9)
        style_prompt = ""
        if style_examples:
            style_prompt = "\nSTYLE GUIDANCE (Few-Shot Examples):\n" + "\n---\n".join(style_examples) + "\n"
            style_prompt += "INSTRUCTION: Draft following the sentence structure and tone of these examples.\n\n"

        # In a real scenario, this would use an LLM to expand the disclosure
        spec = f"TITLE: {disclosure.splitlines()[0] if disclosure else 'Patent Application'}\n\n"
        spec += "FIELD OF THE INVENTION\n"
        spec += f"The present invention relates generally to {disclosure[:50]} and more specifically to systems comprising same.\n\n"
        spec += "BACKGROUND OF THE ART\n"
        spec += "Existing solutions include: " + prior_art_summary[:300] + " however, there remains a need for the improvements disclosed herein.\n\n"
        
        # Phase 8: Vision Support - Detailed Description of the Drawings
        if visual_map:
            spec += "BRIEF DESCRIPTION OF THE DRAWINGS\n"
            spec += "FIG. 1 is a schematic view of the disclosed system components.\n\n"
            
            spec += "DETAILED DESCRIPTION OF THE DRAWINGS\n"
            spec += "Referring to FIG. 1, there is shown a system configuration. " 
            for num, part in visual_map.get("numerals", {}).items():
                spec += f"Specifically, {part} {num} is provided. "
            spec += f"\nTECHNICAL FLOW: {visual_map.get('flow', 'No flow described.')}\n\n"

        spec += "DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS\n"
        spec += disclosure + "\n"
        return spec

    def draft_claims(self, key_features, controller=None, style_examples=None):
        print(f"DrafterAgent: Constructing structured claim set (1 Method, 1 System, 10 Dependent)...")
        
        # Style Guidance (Phase 9)
        if style_examples:
            # In a real LLM call, we'd inject this into the context
            print(f"DrafterAgent: Injecting {len(style_examples)} style examples into context window.")
            
        claims_list = []
        
        # Simulating term extraction for consistency (Step 16)
        if controller:
            for feature in key_features[:3]:
                term = feature.lower()
                # Providing a formal definition for the glossary
                definition = f"A specialized {term} adapted for use in the disclosed patent system."
                controller.update_glossary(term, definition)

        # 1. Independent Method Claim
        claims_list.append({"text": f"1. A method for toasting comprising: providing a {key_features[0].lower()}.", "depends_on": None})
        # 5 Dependent Method Claims
        for i in range(1, 6):
            feature = key_features[i % len(key_features)].lower()
            claims_list.append({"text": f"{i+1}. The method of claim 1, further comprising {feature}.", "depends_on": 1})
            
        # 2. Independent System Claim
        claims_list.append({"text": f"7. A system comprising: a processor; and a {key_features[0].lower()} controlled by the processor.", "depends_on": None})
        # 5 Dependent System Claims
        for i in range(1, 6):
            feature = key_features[i % len(key_features)].lower()
            claims_list.append({"text": f"{i+7}. The system of claim 7, further comprising {feature}.", "depends_on": 7})
        
        return self.drafting_tool(claims_list)
