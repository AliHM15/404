import streamlit as st
from my_button import my_button

def nav_button():
    pages = {
        "home": ("🏠 ", "main.py"),
        "user": ("👤 ", "pages/user_page.py"),
        "challenges": ("⚙️ ", "pages/challenges_page.py"),
        "rewards": ("🏆 ", "pages/rewards_page.py")
    }

    my_button()

    cols = st.columns(len(pages), width="stretch")
    for i, (key, label) in enumerate(pages.items()):
        if cols[i].button(label[0]):
            st.session_state.page = key
            st.switch_page(label[1])