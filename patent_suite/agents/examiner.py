class MockExaminerAgent:
    """
    Role: Adversarial QA / USPTO Examiner.
    Instruction: You are a USPTO Examiner. You hate granting patents. 
    Read the draft and the prior art found by the Searcher. 
    Write a rejection argument that is difficult to overcome.
    """
    def __init__(self):
        pass

    def examine(self, draft_claims, prior_art_results):
        print("MockExaminerAgent: Commencing adversarial review (Searching for reasons to reject)...")
        
        rejections = "--- NON-FINAL OFFICE ACTION ---\n"
        rejections += "SUMMARY: ALL CLAIMS ARE REJECTED.\n\n"
        rejections += "Rejection under 35 U.S.C. 103 (Obviousness):\n"
        rejections += "Claims 1-X are rejected as being unpatentable over the prior art cited by the Applicant.\n\n"
        
        for i, res in enumerate(prior_art_results[:3], 1):
            rejections += f"DETAILED BASIS: Reference {res['id']} ({res['title']}) discloses basic 'toasting' and 'precision heating' concepts.\n"
            rejections += f"While the reference might not explicitly mention '{draft_claims[:20].strip()}', "
            rejections += "it would have been obvious to a POSITA (Person of Ordinary Skill in the Art) to combine these teachings "
            rejections += "to arrive at the claimed invention without undue experimentation.\n\n"
            
        rejections += "CONCLUSION: The application is rejected. The Applicant is encouraged to cancel all claims.\n"
            
        return rejections
