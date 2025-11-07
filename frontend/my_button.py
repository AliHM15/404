import streamlit as st

def my_button():
    st.markdown("""
    <style>
    div.stButton {
       display: flex;
        justify-content: center;  
        align-items: center;      
    }

        
    div.stButton > button {
        background-color: #9ACD32;
        color: white;
        border: none;
        border-radius: 50%;        
        width: 50px;
        height: 50px;
        font-size: 18px;
        cursor: pointer;
    }

    </style>
    """, unsafe_allow_html=True)

