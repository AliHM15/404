import json
import os

def load_users():
    """Load users from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), 'users.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_user(user_id):
    """Get a specific user by ID"""
    users = load_users()
    return users.get(user_id)

def get_all_users():
    """Get all users"""
    return load_users()