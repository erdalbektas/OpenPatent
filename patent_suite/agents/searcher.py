class SearcherAgent:
    """
    Expert in boolean logic and classification codes (CPC/IPC).
    Role: Senior Search Specialist.
    Instruction: Given an invention, formulate search queries. Retrieve results. 
    Summarize why a result might block the invention (Section 102/103 issues).
    """
    def __init__(self, search_tool):
        self.search_tool = search_tool

    def run(self, invention_disclosure):
        print("SearcherAgent: Analyzing disclosure for search strategy...")
        # Mocking sophisticated keyword extraction and boolean logic formulation
        terms = invention_disclosure.lower().split()
        main_subject = terms[0] if terms else "apparatus"
        keywords = f"({main_subject} AND toasting) OR (laser AND precision AND heating)"
        
        print(f"SearcherAgent: Formulating Boolean Query -> {keywords}")
        results = self.search_tool(keywords)
        
        summary = "--- SearcherAgent Analysis (Anticipated Rejections) ---\n"
        for res in results:
            # Mock 102/103 determination
            if "laser" in res['title'].lower() and "toaster" in res['abstract'].lower():
                rejection_type = "35 U.S.C. 102 (Anticipation)"
                reason = "Identical features found in a single reference."
            else:
                rejection_type = "35 U.S.C. 103 (Obviousness)"
                reason = "Differences from prior art would have been obvious to a POSITA."
                
            summary += f"- {res['id']} ({res['title']}): Potentially blocks under {rejection_type}. Reason: {reason}\n"
            
        return summary, results
