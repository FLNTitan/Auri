import streamlit as st
from ideation.generator import generate_ideas

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(
    page_title="Auri | Your AI Social Media Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Professional Custom Styling
# ----------------------------
st.markdown("""
<style>
    /* Main layout container */
    .block-container {
        padding: 2rem 3rem;
        background-color: #F4F7FA;
    }

    /* Sidebar branding */
    [data-testid="stSidebar"] {
        background-color: #1F2235;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] .css-1v3fvcr {
        color: #FFFFFF;
    }

    /* Section headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
    }

    /* Custom card design */
    .idea-card {
        background-color: #FFFFFF;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
        transition: 0.3s ease;
    }

    .idea-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }

    /* Floating assistant chat (optional future) */
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
# Top Hero Section
# ----------------------------
st.markdown("""
    <div style='text-align: center; margin-top: 2rem; margin-bottom: 1rem;'>
        <h1 style='color: #6C63FF; font-size: 2.8rem;'>✨ Auri: Your AI Social Media Copilot</h1>
        <p style='font-size: 1.1rem; color: #1F2937;'>Plan, create, and publish your content with intelligent guidance and powerful creative tools 🚀</p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------
# Ideation Section
# ----------------------------
if section == "🧠 Ideation":
    st.markdown("## 🧠 Content Ideation")
    st.markdown("Let Auri help you spark your next idea. Select a preset or type your own prompt.")

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🎯 Generate content ideas"):
            st.session_state["prompt"] = "Generate 5 content ideas"

    with col2:
        custom = st.text_input("Or describe what you need", placeholder="e.g. Write captions for a fitness post")

    # Results
    if "prompt" in st.session_state or custom:
        prompt = st.session_state.get("prompt", custom)
        st.markdown(f"#### 💡 Auri is thinking about: _{prompt}_")
        ideas = generate_ideas(prompt)

        for idea in ideas:
            st.markdown(f"<div class='idea-card'>🟣 {idea}</div>", unsafe_allow_html=True)

# ----------------------------
# Studio Section Placeholder
# ----------------------------
elif section == "🎨 Studio":
    st.markdown("## 🎨 Studio")
    st.info("Auri's content editor is coming soon. This will be your visual workspace for posts and videos.")

# ----------------------------
# Schedule Section Placeholder
# ----------------------------
elif section == "📆 Schedule":
    st.markdown("## 📆 Scheduling")
    st.info("Here you’ll be able to plan and schedule your social media content visually.")

# ----------------------------
# Analytics Section Placeholder
# ----------------------------
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance here in beautiful charts and reports.")
