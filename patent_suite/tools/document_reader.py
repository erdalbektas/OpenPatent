import re

def read_patent_pdf(filepath):
    """
    Extract text from a patent document (Refined Implementation).
    Identifies 'Claims' section vs 'Specification' section using common markers.
    """
    print(f"Reading patent document: {filepath}")
    
    # In a real scenario, we'd use a PDF library to extract text
    # Here we mock the extracted text content
    raw_text = """
    (12) United States Patent
    (10) Patent No.: US 9,999,999 B2
    
    (54) TITLE: RASTERIZED LASER TOASTING SYSTEM
    
    CROSS-REFERENCE TO RELATED APPLICATIONS
    This application claims priority to...
    
    FIELD OF THE INVENTION
    The present invention relates generally to food preparation...
    
    BACKGROUND OF THE INVENTION
    Conventional toasters use resistive heating wires...
    
    SUMMARY OF THE INVENTION
    The present invention provides a system...
    
    DETAILED DESCRIPTION / SPECIFICATION
    The preferred embodiment includes a laser diode array (102)...
    The laser is configured to scan the surface of the bread (104)...
    The microcontroller (106) regulates the pulse width...
    
    What is claimed is:
    1. A system for toasting bread comprising:
    a laser array; and
    a controller configured to rasterize beams from said array.
    
    2. The system of claim 1, wherein the laser array is infrared.
    """
    
    sections = {
        "specification": "",
        "claims": ""
    }
    
    # Robust section markers
    spec_markers = [r"(?i)DETAILED DESCRIPTION", r"(?i)SPECIFICATION", r"(?i)SUMMARY OF THE INVENTION"]
    claims_markers = [r"(?i)What is claimed is[:]", r"(?i)CLAIMS", r"(?i)The invention claimed is[:]"]
    
    # Identify Specification
    spec_start = -1
    for marker in spec_markers:
        match = re.search(marker, raw_text)
        if match:
            spec_start = match.end()
            break
            
    # Identify Claims
    claims_start = -1
    for marker in claims_markers:
        match = re.search(marker, raw_text)
        if match:
            claims_start = match.start()
            claims_content_start = match.end()
            break
            
    if spec_start != -1:
        end_pos = claims_start if claims_start != -1 else len(raw_text)
        sections["specification"] = raw_text[spec_start:end_pos].strip()
        
    if claims_start != -1:
        sections["claims"] = raw_text[claims_content_start:].strip()
        
    return sections

if __name__ == "__main__":
    data = read_patent_pdf("dummy.pdf")
    print("Specification Sample:", data["specification"][:50])
    print("Claims Sample:", data["claims"][:50])
