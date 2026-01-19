def classify_invention(keywords_or_text):
    """
    Automatically identify the Cooperative Patent Classification (CPC) code.
    Based on keyword matching (Mock implementation).
    """
    print(f"Classifying invention: {keywords_or_text[:50]}...")
    
    # Mock database of CPC codes
    cpc_map = {
        "toaster": "A47J 37/08 - Bread toasters",
        "laser": "H01S 3/00 - Lasers",
        "heating": "H05B 3/00 - Ohmic-resistance heating",
        "software": "G06F 8/00 - Software engineering"
    }
    
    matches = []
    text_lower = keywords_or_text.lower()
    for key, code in cpc_map.items():
        if key in text_lower:
            matches.append(code)
            
    if not matches:
        return ["G06Q 50/00 - Services (General)"]
        
    return matches

if __name__ == "__main__":
    codes = classify_invention("A laser toaster using infrared rasterization")
    print(f"Suggested CPC Codes: {codes}")
