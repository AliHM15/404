import streamlit as st
from navigation import nav_button
from user_utils.users import get_current_user
from user_utils.tags import get_tags_by_category
from user_utils.tags import toggle_user_tag
from buttons import tag_button
import os

st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")

# Force white background and dark text


nav_button()

# TODO: Replace with actual user session handling; keep user_id separate so we can pass it to callbacks
current_user = get_current_user()
user_id = current_user


# Get absolute path - profilepics are in user_utils folder
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_path = os.path.join(base_dir, 'user_utils', current_user.get('profile_picture'))

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(image_path):
        # Read and encode the image
        import base64
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/jpeg;base64,{img_data}" 
                     style="border-radius: 50%; 
                            width: 250px; 
                            height: 250px; 
                            object-fit: cover;
                            display: block;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="display: flex; justify-content: center;">
                <img src="https://via.placeholder.com/250" 
                     style="border-radius: 50%; 
                            width: 250px; 
                            height: 250px; 
                            object-fit: cover;
                            display: block;">
            </div>
            """,
            unsafe_allow_html=True
        )
st.markdown(
    f"""
    <div style="display:flex; justify-content:center; align-items:center;">
        <h1 style="margin:0;">{current_user.get('name')}</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display tags organized by category in columns
st.subheader("Profile Tags")
tags_by_category = get_tags_by_category()
user_tags = current_user.get('tags', []) if current_user else []

# Create three columns for the three categories
category_labels = {
    "interests": "🎯 Interests",
    "living_status": "🏠 Living Status",
    "profession": "💼 Profession"
}

category_cols = st.columns(3)

for idx, (category, label) in enumerate(category_labels.items()):
    with category_cols[idx]:
        st.markdown(f"**{label}**")
        tags = tags_by_category.get(category, [])
        for tag in tags:
            has = tag in user_tags
            tag_button(tag=tag, user_id=user_id, has_tag=has, key=f"tag_{category}_{tag}", on_click=toggle_user_tag)

st.markdown("---")  # Separator after all tags

# Create two columns - left for additional info, right for content
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Statistics")
    # Add stats here later
    pass
        

with right_col:
    st.subheader("User Information")
    # Add user info here later


