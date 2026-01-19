import json
import os

def parse_drawing(image_path):
    """
    Simulates a multimodal LLM (GPT-4o/LLaVA) analyzing a patent drawing.
    Identifies reference numerals and connection flows.
    """
    print(f"VisionParser: Analyzing patent drawing at {image_path}...")
    
    # In a real implementation, this would involve encoding the image and 
    # sending it to a multimodal model with the specified prompt.
    
    # Prompt Strategy: "Analyze this patent drawing. Return a JSON object 
    # mapping Reference Numerals (100, 102...) to Part Names. 
    # Then describe the connection flow."
    
    basename = os.path.basename(image_path).lower()
    
    # Mocking different results based on dummy filenames
    if "toaster" in basename:
        data = {
            "numerals": {
                "100": "Laser Housing",
                "102": "Bread Slot",
                "104": "Rasterizing Mirror",
                "106": "Optical Feedback Sensor"
            },
            "flow": "The Laser Housing 100 directs a beam toward the Rasterizing Mirror 104, which scans the surface of a bread item in the Bread Slot 102, while the Optical Feedback Sensor 106 monitors browning levels."
        }
    else:
        # Default mock for a generic server/database diagram
        data = {
            "numerals": {
                "100": "Server",
                "102": "Database",
                "104": "Load Balancer"
            },
            "flow": "The Load Balancer 104 receives incoming requests and distributes them to the Server 100, which communicates with the Database 102 to retrieve stored records."
        }
        
    return data

if __name__ == "__main__":
    # Mock test
    test_path = "workspaces/samples/fig1_toaster.png"
    result = parse_drawing(test_path)
    print(json.dumps(result, indent=4))
