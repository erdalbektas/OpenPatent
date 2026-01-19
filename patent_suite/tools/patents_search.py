import json
import time
import os
import sys

# Ensure non_patent_search can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from non_patent_search import search_non_patent_literature

def search_prior_art(keywords, date_cutoff=None):
    """
    Search prior art (Refined Mock implementation).
    Connects to mock Google Patents / USPTO data.
    Returns titles and abstracts of the top 10 matches.
    """
    print(f"Searching prior art for: {keywords} (Cutoff: {date_cutoff})")
    time.sleep(1) # Simulate network lag
    
    # Expanded mock results to fulfill the "top 10" requirement
    mock_registry = [
        {"id": "US-1234567-A1", "title": "Infrared Toasting Apparatus", "abstract": "A method for toasting food items using a plurality of infrared emitters arranged in a grid.", "date": "2015-05-20"},
        {"id": "US-7654321-B2", "title": "Laser-Based Material Processing", "abstract": "A system for rasterizing laser beams to heat substrates with high precision.", "date": "2018-11-12"},
        {"id": "EP-9876543-A1", "title": "Non-Contact Heating Device", "abstract": "Device using electromagnetic radiation to heat organic materials without physical contact.", "date": "2010-01-05"},
        {"id": "US-1111111-A1", "title": "Smart Toaster with Feedback Loop", "abstract": "A toaster equipped with optical sensors to monitor browning levels in real-time.", "date": "2020-03-15"},
        {"id": "US-2222222-B1", "title": "Directed Energy Heating System", "abstract": "Apparatus for directing energy beams to specific coordinates on a food item.", "date": "2019-07-22"},
        {"id": "US-3333333-A1", "title": "Automated Bread Browning Control", "abstract": "Computer-controlled heating elements for uniform bread toasting.", "date": "2017-12-01"},
        {"id": "JP-4444444-B2", "title": "High-Efficiency Raster Heating", "abstract": "Method of scanning a surface with a heat source to achieve uniform temperature distribution.", "date": "2016-09-10"},
        {"id": "US-5555555-A1", "title": "Precision Thermal Toaster", "abstract": "Toaster using micro-controller units to execute complex heating patterns.", "date": "2021-01-30"},
        {"id": "US-6666666-B2", "title": "Laser Rastering for Culinary Applications", "abstract": "Using low-power lasers to brown or cook patterns onto dough-based products.", "date": "2022-05-14"},
        {"id": "US-7777777-A1", "title": "Multi-Zone Infrared Cooker", "abstract": "Cooking device with independently controlled infrared zones for variable heating.", "date": "2014-08-08"},
        {"id": "US-8888888-B1", "title": "Optical Sensor for Toaster Safety", "abstract": "Sensors that detect burning and automatically shut off power to avoid fires.", "date": "2013-11-25"}
    ]
    
    # Filter based on keywords (simple mock ranking)
    keywords_list = keywords.lower().split()
    results = []
    for entry in mock_registry:
        score = sum(1 for k in keywords_list if k in entry['title'].lower() or k in entry['abstract'].lower())
        if score > 0:
            entry['relevance_score'] = score
            results.append(entry)
    
    # Sort by score and date
    results.sort(key=lambda x: (x['relevance_score'], x['date']), reverse=True)
    
    return results[:10]

if __name__ == "__main__":
    print("--- Patent Search ---")
    results = search_prior_art("laser toaster", "2024-01-01")
    print(json.dumps(results, indent=2))
    
    print("\n--- Non-Patent Search (Qwen Deep Research) ---")
    non_patent = search_non_patent_literature("laser toaster", session_id="test_v4")
    print(json.dumps(non_patent, indent=2))
