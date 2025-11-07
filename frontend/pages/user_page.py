import streamlit as st
from navigation import nav_button
from user_utils.users import get_user
from user_utils.tags import get_tags
import os

st.set_page_config(page_title="Yippie", page_icon="🎉", layout="centered")

nav_button()

current_user = get_user("user1") #TODO: Replace with actual user session handling

st.title(f"Hello {current_user.get('name')}!")

# Get absolute path - profilepics are in user_utils folder
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_path = os.path.join(base_dir, 'user_utils', current_user.get('profile_picture'))

# Center the image with CSS for round frame
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(image_path):
        st.markdown(
            f"""
            <style>
            .profile-pic {{
                border-radius: 50%;
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 200px;
                height: 200px;
                object-fit: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.image(image_path, width=200, use_container_width=False)
        st.markdown('<style>img {border-radius: 50%; object-fit: cover;}</style>', unsafe_allow_html=True)
    else:
        st.image("https://via.placeholder.com/200", width=200)
        st.markdown('<style>img {border-radius: 50%;}</style>', unsafe_allow_html=True)

# Create two columns - left for tags, right for content
left_col, right_col = st.columns([1, 3])

with left_col:
    st.subheader("Tags")
    tags = get_tags()
    for tag in tags:
        st.button(tag.capitalize(), key=f"tag_{tag}", use_container_width=True)

with right_col:
    st.subheader("User Information")
    # Add user info here later


