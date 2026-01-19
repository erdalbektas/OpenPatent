# utils.py - External functions for the Patent Suite
import os
import json
import re
from .suite_app import WorkspaceManager
from .tools.safe_file_manager import SafeFileManager

def get_workspace_manager():
    return WorkspaceManager()

def verify_workspace_structure(session_id):
    wm = get_workspace_manager()
    session_dir = wm.init_session_workspace(session_id)
    
    expected_folders = ['disclosure', 'references', 'drafts', 'final_export']
    results = {}
    for folder in expected_folders:
        folder_path = os.path.join(session_dir, folder)
        results[folder] = os.path.exists(folder_path)
    
    return session_dir, results

def generate_meta_summary(input_text):
    """
    Mock LLM logic to extract 'Key Features' from the disclosure text.
    In a real implementation, this would call an LLM API.
    """
    # Simple extraction logic for mock
    lines = input_text.split('\n')
    features = [line.strip() for line in lines if line.strip()][:5]
    
    return {
        "title": "Invention Disclosure Summary",
        "key_features": features,
        "status": "Ready for Search"
    }

def scrape_mpep(section_id):
    """
    Mock Scraper for MPEP Sections.
    Returns content for Sections 2100 (Patentability) and 700 (Examination).
    """
    mock_data = {
        "2100": [
            {"section": "2103", "title": "Patent Eligibility", "content": "Laws of nature, natural phenomena, and abstract ideas are not patentable."},
            {"section": "2106", "title": "Subject Matter Eligibility", "content": "Specific guidance on software and abstract ideas (Alice check)."},
            {"section": "2111", "title": "Claim Interpretation", "content": "Claims must be given their broadest reasonable interpretation (BRI)."}
        ],
        "700": [
            {"section": "706", "title": "Rejection of Claims", "content": "Basis for rejecting claims under 35 U.S.C. 102 and 103."},
            {"section": "701", "title": "Order of Examination", "content": "Instructions on the order in which patent applications are examined."},
            {"section": "707", "title": "Examiner's Letter or Action", "content": "Guidance on writing rejections and responses."}
        ]
    }
    return mock_data.get(section_id, [])

def index_mpep():
    """
    Indexes MPEP Sections 2100 and 700 into a local JSON store.
    """
    print("Indexing MPEP Sections 2100 and 700...")
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpep_index.json')
    
    sections_2100 = scrape_mpep("2100")
    sections_700 = scrape_mpep("700")
    
    all_sections = sections_2100 + sections_700
    with open(index_path, 'w') as f:
        json.dump(all_sections, f, indent=4)
    
    print(f"Successfully indexed {len(all_sections)} sections to {index_path}.")
    return index_path

def search_mpep(query, top_k=2):
    """
    Search indexed MPEP sections for relevance.
    """
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpep_index.json')
    if not os.path.exists(index_path):
        index_mpep()
        
    with open(index_path, 'r') as f:
        docs = json.load(f)
        
    query = query.lower()
    results = []
    for doc in docs:
        if query in doc['content'].lower() or query in doc['title'].lower():
            results.append(doc)
            
    return results[:top_k]

def transcribe_audio(audio_file_path):
    """
    Mock implementation of OpenAI Whisper transcription.
    """
    import time
    print(f"Transcribing audio file: {audio_file_path}")
    # Simulate transcription delay
    time.sleep(1)
    
    # Simple mock transcription result
    return "A laser-based toaster that uses a micro-rasterizer for precise bread patterns."

def get_style_examples(query, count=3):
    """
    Retrieves high-quality 'Gold Standard' patent examples from the local dataset.
    In a real app, this would use vector search. Here we simulate it by reading 
    the harvested files.
    """
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'gold_standard_patents')
    if not os.path.exists(base_dir):
        return []
    
    examples = []
    # Simplified mock retrieval: just take the first few files
    files = [f for f in os.listdir(base_dir) if f.endswith('.txt')]
    for file_name in files[:count]:
        with open(os.path.join(base_dir, file_name), 'r') as f:
            examples.append(f.read())
            
    return examples

def get_safe_file_manager(session_id):
    """
    Returns a SafeFileManager instance for the given session.
    """
    wm = get_workspace_manager()
    session_dir = wm.init_session_workspace(session_id)
    drafts_dir = os.path.join(session_dir, 'drafts')
    return SafeFileManager(drafts_dir)
