#!/usr/bin/env python3
import os
import sys
import json
import argparse

# Setup path to include patent_suite
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patent_suite.suite_app')
import django
django.setup()

from patent_suite.suite_app import WorkspaceManager
from patent_suite.utils import generate_meta_summary

def ingest(session_id, input_text):
    print(f"Ingesting disclosure for session: {session_id}")
    
    wm = WorkspaceManager()
    session_dir = wm.init_session_workspace(session_id)
    
    # 1. Save to /disclosure/notes.txt
    disclosure_dir = os.path.join(session_dir, 'disclosure')
    notes_path = os.path.join(disclosure_dir, 'notes.txt')
    with open(notes_path, 'w') as f:
        f.write(input_text)
    
    print(f"Notes saved to {notes_path}")
    
    # 2. Trigger LLM Summary via utils
    print("Extracting Key Features (LLM Summary)...")
    summary = generate_meta_summary(input_text)
    
    meta_path = os.path.join(disclosure_dir, 'meta.json')
    with open(meta_path, 'w') as f:
        json.dump(summary, f, indent=4)
    
    print(f"Meta data saved to {meta_path}")
    return session_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest an invention disclosure.")
    parser.add_argument("--session", default="default_v2", help="Session ID")
    parser.add_argument("--text", help="Disclosure text")
    parser.add_argument("--file", help="Path to disclosure file")
    
    args = parser.parse_args()
    
    text = args.text
    if args.file and os.path.exists(args.file):
        with open(args.file, 'r') as f:
            text = f.read()
    
    if not text:
        text = input("Enter disclosure text: ")
        
    ingest(args.session, text)
