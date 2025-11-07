import json
import os

def load_tags():
    """Load tags from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), 'tags.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_tags():
    """Get list of tags"""
    data = load_tags()
    return data.get("tags", [])