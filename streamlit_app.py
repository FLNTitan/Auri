
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Auri – Your AI Content Copilot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inject global styles
st.markdown("""
    <style>
        html, body, [class*="css"] {
            background-color: #F4F7FA !important;
            font-family: 'Segoe UI', sans-serif;
        }
        h1 {
            color: #6C63FF;
            font-size: 2.6rem;
        }
        h3 {
            color: #1F2937;
        }
        .stTextInput input {
            background-color: #ffffff !important;
            color: #1F2937 !important;
            border-radius: 6px;
            padding: 0.5rem;
        }
        .stButton button {
            background-color: #6C63FF !important;
            color: white !important;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 0.5rem;
        }
        .stButton button:hover {
            background-color: #574fd6 !important;
        }
    </style>
""", unsafe_allow_html=True)

# UI Content
st.markdown("## 👋 Hey there, I’m Auri")
st.markdown("### What do you want to achieve today?")

col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Give me new content ideas"):
        st.session_state['prompt'] = "Generate 5 content ideas for my niche"
with col2:
    custom_prompt = st.text_input("Or type your own request", "")

# Display result
if "prompt" in st.session_state or custom_prompt:
    user_prompt = st.session_state.get('prompt', custom_prompt)
    st.markdown(f"💡 **Auri’s thinking about:** _{user_prompt}_")

    # Simulated idea output
    st.markdown("""
    <ul>
        <li>🎬 A simple 15s reel showing 'before vs after' transformation</li>
        <li>📈 A hook: 'Most people ignore this tip…'</li>
        <li>🤯 A myth-busting clip: 'You thought this was healthy?'</li>
        <li>🔁 A stitch: 'Respond to this trending sound with your twist'</li>
        <li>🧪 Try-on challenge or 3-part storytelling hook</li>
    </ul>
    """, unsafe_allow_html=True)
