import streamlit as st
from navigation import nav_button

st.set_page_config(page_title="Rewards", page_icon="🎁", layout="centered")



nav_button()
st.title("Rewards")

# Display coin gif
st.image("misc/coin.gif", use_container_width=True)
