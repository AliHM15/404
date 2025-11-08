import streamlit as st
from navigation import nav_button

st.set_page_config(page_title="Challenges", page_icon="🏅", layout="centered")


nav_button()
st.title("Challenges")

# Display windturbine gif
st.image("misc/windturbine.gif", use_container_width=True)



