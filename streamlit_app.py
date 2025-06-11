import streamlit as st
from ideation.generator import generate_ideas

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(
    page_title="Auri | Your AI Social Media Copilot",
    page_icon="✨",
    layout="wide",  # wide to allow dashboard feel
    initial_sidebar_state="expanded"
)

# ----------------------------
# Custom Styling
# ----------------------------
st.markdown("""
<style>
    .block-container {
        padding: 2rem 3rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1F2235;
        color: #FFFFFF;
    }

    /* Card design */
    .idea-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }

    /* Chat Assistant floating container */
    .assistant-chat {
        position: fixed;
        bottom: 20px;
        right: 30px;
        width: 320px;
        max-height: 400px;
        overflow-y: auto;
        background-color: #F4F7FA;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        padding: 1rem;
        z-index: 9999;
    }

    .assistant-chat h4 {
        color: #6C63FF;
        margin-bottom: 0.5rem;
    }

    .assistant-toggle {
        position: fixed;
        bottom: 20px;
        right: 30px;
        background-color: #6C63FF;
        color: white;
        padding: 0.75rem 1rem;
        border: none;
        border-radius: 999px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        cursor: pointer;
        z-index: 10000;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar Navigation
# ----------------------------
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    section = st.radio("Jump to", ["🧠 Ideation", "🎨 Studio", "📆 Schedule", "📊 Analytics"])

# ----------------------------
# Top Hero Header
# ----------------------------
st.markdown(
    "<h1 style='text-align: center; color: #6C63FF;'>✨ Auri: Your AI Social Media Copilot</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Plan, create, and publish with your AI assistant 🚀</p>",
    unsafe_allow_html=True
)

# ----------------------------
# Ideation Section
# ----------------------------
if section == "🧠 Ideation":
    st.markdown("### What do you want to create today?")
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🎯 Give me new content ideas"):
            st.session_state["prompt"] = "Generate 5 content ideas"

    with col2:
        custom = st.text_input("Or describe it in your own words")

    if "prompt" in st.session_state or custom:
        prompt = st.session_state.get("prompt", custom)
        st.markdown(f"💡 **Auri's thinking about:** _{prompt}_")
        ideas = generate_ideas(prompt)

        for idea in ideas:
            st.markdown(f"<div class='idea-card'>🟣 {idea}</div>", unsafe_allow_html=True)

# ----------------------------
# Placeholder Sections
# ----------------------------
elif section == "🎨 Studio":
    st.markdown("## 🎨 Editor Studio (Coming Soon...)")
    st.info("This section will host the AI-powered content editor.")

elif section == "📆 Schedule":
    st.markdown("## 📆 Schedule Planner (Coming Soon...)")
    st.info("This will show a content calendar and let you schedule posts.")

elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics (Coming Soon...)")
    st.info("Here you’ll find charts and summaries of your content performance.")

# ----------------------------
# Persistent Floating Assistant (Toggleable)
# ----------------------------
with st.expander("💬 Auri Assistant"):
    st.markdown("**Need help with anything? Ask Auri below!**")
    chat_input = st.text_input("Ask Auri something...", key="chat_input")
    if chat_input:
        st.markdown(f"**🧠 Auri says:** _Here's a thought on: '{chat_input}'..._")
        st.markdown("> 🎯 _This is where the assistant's natural language response would appear._")
