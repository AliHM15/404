import streamlit as st

st.set_page_config(page_title="Demo", page_icon="🤖", layout="centered")

st.title("Minimal Streamlit Page")
name = st.text_input("Name")
if name:
    st.write(f"Hello, {name}!")

