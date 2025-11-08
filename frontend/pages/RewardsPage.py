import streamlit as st
from components.spinning_wheel import spinning_wheel

st.title("🎁 Yippie Rewards Wheel")

st.write("Spin the wheel to discover your exclusive reward!")

# Custom rewards wheel with controlled outcome
reward_items = [
    "Free Month of Energy",
    "20% Bill Discount",
    "$100 Gift Card",
    "Priority Support",
    "Solar Panel Consultation",
    "Energy Efficiency Audit",
    "Smart Home Device",
    "VIP Customer Status"
]

st.write("**Click SPIN to win your reward!**")
result = spinning_wheel(items=reward_items, target_index=2)  # Always stops on "$100 Gift Card"

if result:
    st.success(f"🎉 Congratulations! You won: **{result}**")
    st.balloons()
