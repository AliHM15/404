import streamlit as st
from sidebar import show_sidebar
from navigation import nav_button
from user_utils.users import get_current_user
import os
import base64


st.set_page_config(page_title="Yippie", page_icon="🎉", layout="centered")



nav_button()
st.title("Homepage")

# Get current user data
current_user = get_current_user()

# Get user's saved kWh
saved_kwh = current_user.get('kwh', 0)
saved_co2 = current_user.get('co2', 0)

# Goal for the progress circle (adjust as needed)
kwh_goal = 500

# Calculate iteration (how many times the goal has been reached)
iteration = saved_kwh // kwh_goal
current_cycle_kwh = saved_kwh % kwh_goal

# Calculate percentage based on current cycle
kwh_percentage = (current_cycle_kwh / kwh_goal) * 100

# Determine which tree image to show based on progress in current cycle
if kwh_percentage < 20:  # Less than 1/5
    tree_num = 1
elif kwh_percentage < 40:  # Less than 2/5
    tree_num = 2
elif kwh_percentage < 60:  # Less than 3/5
    tree_num = 3
elif kwh_percentage < 80:  # Less than 4/5
    tree_num = 4
else:  # 4/5 or more
    tree_num = 5

# Load the tree image
tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tree', f'tree{tree_num}.png')
if os.path.exists(tree_path):
    with open(tree_path, "rb") as img_file:
        tree_img_data = base64.b64encode(img_file.read()).decode()
else:
    tree_img_data = None

# Create circular progress bar with tree image using SVG
radius = 100
circumference = 2 * 3.14159 * radius
offset = circumference - (kwh_percentage / 100) * circumference

if tree_img_data:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin: 30px 0;">
            <svg width="280" height="280" style="transform: rotate(-90deg);">
                <!-- Background circle -->
                <circle cx="140" cy="140" r="{radius}" 
                        stroke="#e0e0e0" 
                        stroke-width="20" 
                        fill="none"/>
                <!-- Progress circle -->
                <circle cx="140" cy="140" r="{radius}" 
                        stroke="#4CAF50" 
                        stroke-width="20" 
                        fill="none"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{offset}"
                        stroke-linecap="round"
                        style="transition: stroke-dashoffset 0.5s ease;"/>
                <!-- Tree image in center (rotated back) -->
                <image x="65" y="65" width="150" height="150" 
                       href="data:image/png;base64,{tree_img_data}"
                       transform="rotate(90 140 140)"
                       style="pointer-events: none;"/>
            </svg>
            <p style="margin-top: 5px; color: #666; font-size: 14px;">Goal: {kwh_goal} kWh; Current {current_cycle_kwh} kWh</p>
            <p style="margin-top: 10px; font-size: 24px; font-weight: bold; color: #333;">Total {saved_kwh} kWh saved</p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("Tree image not found!")

col1, col2 = st.columns(2)

# Display additional metrics
with col1:
    st.metric("CO₂ Reduced", f"{saved_co2} kg")

with col2:
    st.metric("Total Points", current_user.get('points', 0))

if "page" not in st.session_state:
    st.session_state.page = "home"



