import re
import json

def split_into_elements(text):
    """
    Splits a claim into atomic elements (limitation-level).
    Heuristic: split by commas, semicolons, and certain keywords like 'comprising', 'including'.
    """
    # Remove numbering if present (e.g., "1. A method...")
    text = re.sub(r'^\d+\.\s*', '', text)
    
    # Split by major delimiters
    # Atomic elements are often separated by ", ", "; ", or phrases like "comprising "
    delimiters = r'[,;]|\bcomprising\b|\bincluding\b|\balso\s+comprising\b|\bfurther\s+comprising\b'
    raw_elements = re.split(delimiters, text, flags=re.IGNORECASE)
    
    # Clean up whitespace and remove empty strings
    elements = [e.strip() for e in raw_elements if e.strip()]
    return elements

def calculate_similarity(element1, element2):
    """
    Mock cosine similarity using word overlap.
    In a real app, this would use sentence-transformers or embedding models.
    """
    words1 = set(re.findall(r'\b\w+\b', element1.lower()))
    words2 = set(re.findall(r'\b\w+\b', element2.lower()))
    
    if not words1 or not words2:
        return 0.0
        
    intersection = words1.intersection(words2)
    # Simple overlap coefficient as a similarity proxy
    similarity = len(intersection) / max(len(words1), len(words2))
    return similarity

def map_claims(user_claim_text, prior_art_text):
    """
    Maps atomic elements of a user claim to a prior art reference.
    """
    print("ClaimMapper: Aligning user claim elements against prior art...")
    
    user_elements = split_into_elements(user_claim_text)
    prior_elements = split_into_elements(prior_art_text)
    
    mapping = {}
    threshold = 0.6  # Similarity threshold
    
    for u_el in user_elements:
        best_match = None
        best_score = 0.0
        
        for p_el in prior_elements:
            score = calculate_similarity(u_el, p_el)
            if score > best_score:
                best_score = score
                best_match = p_el
                
        if best_score >= threshold:
            mapping[u_el] = {
                "match": best_match,
                "similarity": round(best_score * 100, 1),
                "status": "OVERLAP"
            }
        else:
            mapping[u_el] = {
                "match": None,
                "similarity": round(best_score * 100, 1),
                "status": "NOVELTY DETECTED"
            }
            
    return mapping

if __name__ == "__main__":
    # Test case
    user_claim = "1. A toaster comprising: a laser pattern radiator; and a bread carriage."
    prior_art = "A heating device including a bread carriage and a nichrome wire heating element."
    
    results = map_claims(user_claim, prior_art)
    print(json.dumps(results, indent=4))
