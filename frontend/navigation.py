import streamlit as st
from buttons import menu_button_style
from buttons import menu_button

def nav_button():
    pages = {
        "home": ("🏠 ", "main.py"),
        "user": ("👤 ", "pages/user_page.py"),
        "challenges": ("🏅 ", "pages/challenges_page.py"),
        "rewards": ("🎁 ", "pages/rewards_page.py")
    }

    # Custom CSS for navigation buttons only
    st.markdown("""
    <style>
    .nav-btn-custom {
        background-color: #9ACD32;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 18px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        margin: 0 auto;
    }
    .nav-btn-custom:hover {
        background-color: #8FBC29;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(pages))
    for col, (key, (emoji, path)) in zip(cols, pages.items()):
        with col:
            # Check if this button was clicked via query params
            params = st.query_params
            if params.get("nav") == key:
                # Clear the param and navigate
                params.clear()
                st.switch_page(path)
            
            # Create HTML button with unique identifier
            button_html = f"""
            <div style="display: flex; justify-content: center;">
                <a href="?nav={key}" target="_self" class="nav-btn-custom">
                    {emoji}
                </a>
            </div>
            """
            st.markdown(button_html, unsafe_allow_html=True)