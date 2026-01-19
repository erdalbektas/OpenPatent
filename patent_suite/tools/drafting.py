def write_claim_set(claims_list):
    """
    Format a set of claims.
    Automatically numbers claims (1, 2, 3...) and formats dependencies ("The widget of Claim 1...").
    Expected format for claims_list: 
    [{"text": "A widget comprising X...", "depends_on": None},
     {"text": "The widget of [PARENT], where X is Y...", "depends_on": 1}]
    """
    print("Formatting claim set...")
    formatted_claims = []
    
    for i, claim in enumerate(claims_list, 1):
        text = claim["text"]
        depends_on = claim.get("depends_on")
        
        # If it's a dependent claim and has a placeholder for the parent claim number
        if depends_on is not None and "[PARENT]" in text:
            text = text.replace("[PARENT]", f"Claim {depends_on}")
        
        prefix = f"{i}. "
        formatted_claims.append(f"{prefix}{text}")
        
    return "\n\n".join(formatted_claims)

if __name__ == "__main__":
    test_claims = [
        {"text": "A system comprising a laser and a toaster.", "depends_on": None},
        {"text": "The system of [PARENT], further comprising a rasterizer.", "depends_on": 1},
        {"text": "The system of [PARENT], where the rasterizer is a micro-rasterizer.", "depends_on": 2}
    ]
    print(write_claim_set(test_claims))
