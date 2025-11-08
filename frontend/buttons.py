import uuid
import streamlit as st

def menu_button_style():
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
    
def menu_button(label="+", key: str | None = None) -> bool:
    """
    Render a circular navigation button using Streamlit's native button.
    Returns True when the button is clicked.
    Styling is applied in navigation.py to avoid affecting other buttons.
    """
    uid = key or f"menu-btn-{uuid.uuid4().hex}"
    return st.button(label, key=uid, use_container_width=False)


def tag_button(tag: str, user_id: str, has_tag: bool = False, key: str | None = None, on_click=None):
    """Render a tag button using Streamlit's native `st.button` so it behaves
    like other Streamlit widgets (no new tabs) and respects global CSS for layout.

    - tag: raw tag string (e.g. 'technology')
    - user_id: id string passed to the on_click callback as first arg
    - has_tag: whether the user currently has this tag (used to change label)
    - key: optional Streamlit widget key
    - on_click: optional callback (callable) which should accept (user_id, tag)

    Returns the boolean result from streamlit.button (True if clicked this run).
    """
    label = f"✅ {tag.capitalize()}" if has_tag else f"❌ {tag.capitalize()}"
    k = key or f"tag_{tag}"
    if callable(on_click):
        return st.button(label, key=k, on_click=on_click, args=(user_id, tag))
    return st.button(label, key=k)

