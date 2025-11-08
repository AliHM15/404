import json
import os
import streamlit as st

def load_tags():
    """Load tags from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), 'tags.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_tags():
    """Get list of all tags (backward compatibility)"""
    data = load_tags()
    # Combine all tags from all categories
    all_tags = []
    all_tags.extend(data.get("interests", []))
    all_tags.extend(data.get("living_status", []))
    all_tags.extend(data.get("profession", []))
    return all_tags

def get_tags_by_category():
    """Get tags organized by category"""
    return load_tags()

def get_category_tags(category):
    """Get tags for a specific category (interests, living_status, or profession)"""
    data = load_tags()
    return data.get(category, [])

def user_has_tag(user_tags, tag):
    """Check if user has a specific tag"""
    return tag in user_tags
def _users_file_path():
    return os.path.join(os.path.dirname(__file__), 'users.json')


def load_users():
    """Load users from users.json"""
    file_path = _users_file_path()
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_users(data):
    """Save users dict back to users.json"""
    file_path = _users_file_path()
    # write atomically by writing to a temp file then replacing
    tmp_path = file_path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    os.replace(tmp_path, file_path)


def toggle_user_tag(user_id, tag):
    """Toggle a tag for the given user id in users.json.

    Accepts either a user id string or a user dict (will attempt to resolve id/email).

    If the tag exists on the user, remove it. Otherwise, add it.
    Returns the updated list of tags for the user.
    """
    # tolerate being passed a user dict accidentally
    if isinstance(user_id, dict):
        maybe = user_id.get('id') or user_id.get('user_id') or user_id.get('username')
        if maybe is None and 'email' in user_id:
            # try to resolve id by email
            users_tmp = load_users()
            for uid_tmp, u_tmp in users_tmp.items():
                if u_tmp.get('email') == user_id.get('email'):
                    maybe = uid_tmp
                    break
        user_id = maybe

    users = load_users()
    if user_id not in users:
        raise KeyError(f"User id '{user_id}' not found in users.json")

    user = users[user_id]
    user_tags = user.get('tags', [])

    if tag in user_tags:
        # remove the tag
        user_tags = [t for t in user_tags if t != tag]
    else:
        # add the tag
        user_tags = user_tags + [tag]

    # assign back and save
    user['tags'] = user_tags
    users[user_id] = user
    save_users(users)

    return user_tags


def on_tag_click(user, tag):
    """Callback expected when a tag is clicked in the UI.

    `user` may be either a user dict containing an "id" key, or a string user id.
    This function will toggle the tag and return the updated tags for convenience.
    """
    # allow either a dict with 'id' or a direct user id string
    if isinstance(user, dict):
        user_id = user.get('id') or user.get('user_id') or user.get('username')
        # if no explicit id keys, try name-based lookup (not ideal but tolerant)
        if user_id is None and 'email' in user:
            # try to find matching user id by email
            users = load_users()
            for uid, u in users.items():
                if u.get('email') == user.get('email'):
                    user_id = uid
                    break
    else:
        user_id = user

    if user_id is None:
        raise ValueError('Could not determine user id for on_tag_click')

    return toggle_user_tag(user_id, tag)
