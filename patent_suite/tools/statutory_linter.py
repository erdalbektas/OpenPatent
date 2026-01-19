import json
import os
import re

def check_indefiniteness(text):
    """
    Scans generated text for a blocklist of dangerous patent words (Definiteness Check).
    """
    print("Statutory Linter: Scanning for vague language (§112 compliance)...")
    
    asset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'banned_words.json')
    
    if not os.path.exists(asset_path):
        print(f"Warning: Banned words asset not found at {asset_path}")
        return []

    with open(asset_path, 'r') as f:
        banned_words = json.load(f)

    errors = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines, 1):
        for word, suggestion in banned_words.items():
            # Case-insensitive word boundary match
            if re.search(r'\b' + re.escape(word) + r'\b', line, re.IGNORECASE):
                errors.append({
                    "line": i,
                    "word": word,
                    "error": f"Line {i} uses '{word}'. {suggestion}"
                })
                
    return errors

if __name__ == "__main__":
    sample = "1. A system including approximately five lasers and a user-friendly interface."
    results = check_indefiniteness(sample)
    for err in results:
        print(err["error"])
