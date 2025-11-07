import streamlit as st

def show_sidebar():
    st.sidebar.title("Navigation")

    st.sidebar.page_link("pages/UserPages.py", label="User")

    st.sidebar.page_link("pages/RewardsPage.py", label="Tokens" )

    st.sidebar.page_link("pages/ChallengesPage.py", label="Rewards")