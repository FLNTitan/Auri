import streamlit as st
from ideation.generator import generate_ideas

# Page setup
st.set_page_config(
    page_title="Auri | Your AI Social Media Copilot",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="auto"
)

# Optional: styling enhancements for padding and result card
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }
    .idea-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown(
    "<h1 style='text-align: center; color: #6C63FF;'>✨ Auri: Your AI Social Media Copilot</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Let’s create something amazing together 🚀</p>",
    unsafe_allow_html=True
)

# Prompt section
st.markdown("### What do you want to achieve today?")
col1, col2 = st.columns(2)

if col1.button("🎯 Give me new content ideas"):
    st.session_state["prompt"] = "Generate 5 content ideas"

custom = col2.text_input("Or type your own request")

# Result section
if "prompt" in st.session_state or custom:
    prompt = st.session_state.get("prompt", custom)
    st.markdown(f"💡 **Auri's thinking about:** _{prompt}_")
    ideas = generate_ideas(prompt)

    for idea in ideas:
        st.markdown(f"<div class='idea-card'>🟣 {idea}</div>", unsafe_allow_html=True)
