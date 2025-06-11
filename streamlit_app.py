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
# Global Custom Styling
# ----------------------------
st.markdown("""
<style>
    /* Layout spacing */
    .block-container {
        padding: 2rem 3rem;
        background-color: #F4F7FA;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1F2235;
    }

    /* Sidebar text fixes */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .markdown-text-container,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* Selected radio option styling */
    section[data-testid="stSidebar"] label[data-selected="true"] {
        color: #6C63FF !important;
        font-weight: 600;
    }

    /* Card design */
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
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar Navigation & Branding
# ----------------------------
with st.sidebar:
    # Centered logo using st.image (local file)
    st.image("auri_logo_circular.png", width=120)

    # Sidebar styling
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                color: #FFFFFF;
            }

            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] .markdown-text-container {
                color: #FFFFFF !important;
            }

            section[data-testid="stSidebar"] .stRadio label {
                color: #FFFFFF !important;
                font-size: 1.4rem !important;
                line-height: 1.6rem;
            }

            section[data-testid="stSidebar"] label[data-selected="true"] {
                color: #6C63FF !important;
                font-weight: 700;
            }

            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
                gap: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧭 Navigation")
    section = st.radio(
        "Jump to",
        ["🧠 Content Ideas", "🎨 Editing Studio", "📆 Scheduling", "📊 Analytics"],
    )



# ----------------------------
# Hero Section
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
if section == "🧠 Content Ideas":
    st.markdown("## 🧠 Content Ideation")
    st.markdown("Let Auri help you spark your next idea. Select a preset or type your own prompt.")

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🎯 Generate content ideas"):
            st.session_state["prompt"] = "Generate 5 content ideas"

    with col2:
        custom = st.text_input("Or describe what you need", placeholder="e.g. Write captions for a fitness post")

    if "prompt" in st.session_state or custom:
        prompt = st.session_state.get("prompt", custom)
        st.markdown(f"#### 💡 Auri is thinking about: _{prompt}_")
        ideas = generate_ideas(prompt)

        for idea in ideas:
            st.markdown(f"<div class='idea-card'>🟣 {idea}</div>", unsafe_allow_html=True)

# ----------------------------
# Studio Section Placeholder
# ----------------------------
elif section == "🎨 Editing Studio":
    st.markdown("## 🎨 Editing Studio")
    st.info("Auri's content editor is coming soon. This will be your visual workspace for posts and videos.")

# ----------------------------
# Schedule Section Placeholder
# ----------------------------
elif section == "📆 Scheduling":
    st.markdown("## 📆 Scheduling")
    st.info("Here you’ll be able to plan and schedule your social media content visually.")

# ----------------------------
# Analytics Section Placeholder
# ----------------------------
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance here in beautiful charts and reports.")
