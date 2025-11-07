import streamlit as st
from sidebar import show_sidebar
from navigation import nav_button


st.set_page_config(page_title="Yippie", page_icon="🎉", layout="centered")

nav_button()
st.title("Homepage")
name = st.text_input("Name")
if name:
    st.write(f"Hello, {name}!")


col1, col2 = st.columns(2)
if "page" not in st.session_state:
    st.session_state.page = "home"



