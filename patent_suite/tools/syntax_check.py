import re

def check_antecedent_basis(claims_text):
    """
    Check for antecedent basis errors in a set of claims.
    Logic: If 'the [noun]' or 'said [noun]' is used, 'a [noun]' or 'an [noun]' 
    must have been used previously in the claim or parent chain.
    """
    print("Checking antecedent basis...")
    errors = []
    
    # Split by claim numbers (e.g., '1. ', '2. ')
    claims = re.split(r'\n\s*\d+\.\s+', "\n" + claims_text)
    claims = [c.strip() for c in claims if c.strip()]
    
    introduced_terms = set()
    
    for i, claim in enumerate(claims, 1):
        # Normalize whitespace
        claim_clean = re.sub(r'\s+', ' ', claim)
        
        # 1. Mark terms introduced with 'a' or 'an' in the CURRENT claim first
        introductions = re.findall(r'\ba(?:n)?\s+([a-zA-Z]+)\b', claim_clean, re.IGNORECASE)
        for term in introductions:
            introduced_terms.add(term.lower())

        # 2. Find all instances of 'the [word]' or 'said [word]'
        # We simplify to single words for this mock, but real tools use phrase parsing.
        references = re.findall(r'\b(?:the|said)\s+([a-zA-Z]+)\b', claim_clean, re.IGNORECASE)
        
        for term in references:
            term_lower = term.lower()
            # Special case: 'Claim' as in 'Claim 1' is often exempt or handled differently
            if term_lower == 'claim':
                continue
                
            if term_lower not in introduced_terms:
                errors.append(f"Error: Lacks Antecedent Basis - 'the {term}'")
            
    return {
        "errors_count": len(errors),
        "errors": list(dict.fromkeys(errors)) # Deduplicate
    }

if __name__ == "__main__":
    sample_claims = """
    1. A system comprising a laser and a toaster.
    2. The system of Claim 1, where the lever is activated.
    """
    results = check_antecedent_basis(sample_claims)
    print(results)
