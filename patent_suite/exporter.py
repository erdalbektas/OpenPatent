import os

def export_patent_application(session_id, drafts_dir, final_export_dir):
    """
    Combines text files in /drafts into a standard patent application format.
    Headers: Field of Invention, Background, Summary, Specification, Claims.
    """
    print(f"Exporting patent application for {session_id}...")
    
    if not os.path.exists(final_export_dir):
        os.makedirs(final_export_dir)
        
    final_content = []
    final_content.append("TITLE: INFRARED LASER TOASTING SYSTEM\n")
    final_content.append("="*40 + "\n")
    
    # In a real scenario, we'd read individual files from drafts_dir
    # For this simulation, we'll construct it
    sections = [
        "FIELD OF THE INVENTION",
        "BACKGROUND OF THE INVENTION",
        "SUMMARY OF THE INVENTION",
        "DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS",
        "CLAIMS"
    ]
    
    for section in sections:
        final_content.append(f"\n[{section}]\n")
        # Mocking content retrieval
        filename = section.lower().replace(" ", "_") + ".txt"
        file_path = os.path.join(drafts_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                final_content.append(f.read())
        else:
            final_content.append(f"Content for {section} pending review.\n")
            
    final_path = os.path.join(final_export_dir, "final_application.txt")
    with open(final_path, 'w') as f:
        f.writelines(final_content)
        
    print(f"Application exported to: {final_path}")
    return final_path

if __name__ == "__main__":
    export_patent_application("test_v1", "./drafts", "./final_export")
