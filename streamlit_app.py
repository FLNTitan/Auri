import streamlit as st
from ideation.generator import generate_ideas
from modules.script import generate_script
from modules.thumbnail import generate_thumbnail
from modules.scheduler import schedule_post

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
    .block-container {
        padding: 2rem 3rem;
        background-color: #F4F7FA;
    }

    [data-testid="stSidebar"] {
        background-color: #1F2235;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .markdown-text-container,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
        font-size: 1.4rem !important;
        line-height: 1.8rem;
        display: flex;
        align-items: center;
    }

    section[data-testid="stSidebar"] label[data-selected="true"] {
        color: #6C63FF !important;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0.75rem;
    }

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
    logo_col = st.columns([1, 2, 1])[1]
    with logo_col:
        st.image("auri_logo_circular.png", width=120)

    st.markdown("## 🧽 Navigation")
    section = st.radio(
        "Jump to",
        ["🧠 Content Ideas", "🎨 Editing Studio", "🗖️ Posting & Scheduling", "📊 Analytics"]
    )

# ----------------------------
# Helper Function
# ----------------------------
def parse_steps(raw_response: str) -> list:
    lines = raw_response.strip().split("\n")
    steps = []
    for line in lines:
        if line.strip() == "":
            continue
        if any(line.lstrip().startswith(f"{i}.") for i in range(1, 100)):
            steps.append({"title": line.strip().split('.', 1)[-1].strip(), "description": ""})
        else:
            if steps:
                steps[-1]["description"] += " " + line.strip()
    return steps

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
    st.markdown("Kickstart your workflow with a smart recipe or describe your goal in plain English.")

    with st.expander("🌍 Quick Start Recipes"):
        cols = st.columns(3)
        if cols[0].button("\U0001f4c8 Viral TikTok Sprint"):
            st.session_state["prompt"] = "Plan 3 viral TikTok posts with script, thumbnail, and schedule"
        if cols[1].button("\U0001f3a8 Weekend Reel Builder"):
            st.session_state["prompt"] = "Create 2 weekend Instagram Reels with catchy hooks and music"
        if cols[2].button("\U0001f3a7 YouTube-to-Short"):
            st.session_state["prompt"] = "Repurpose latest YouTube video into 3 Shorts with new captions"

    user_prompt = st.text_input("Or describe your goal...", placeholder="e.g. Turn my last 2 tweets into a carousel and reel")

    if "prompt" in st.session_state or user_prompt:
        full_prompt = st.session_state.get("prompt", user_prompt)
        st.markdown(f"#### 💡 Auri is preparing your flow: _{full_prompt}_")
        raw = generate_ideas(full_prompt)
        steps = parse_steps("\n".join(raw))
        st.session_state["flow"] = steps

        st.markdown("---")
        st.markdown("### 🔄 Workflow Preview")
        for idx, step in enumerate(steps, 1):
            st.markdown(f"**Step {idx}: {step['title']}**")
            if step["description"]:
                st.caption(step["description"])
            if st.button(f"▶ Run Step {idx}", key=f"run_step_{idx}"):
                with st.spinner("Running..."):
                    title = step["title"].lower()
                    if "script" in title:
                        st.success(generate_script(step["description"]))
                    elif "thumbnail" in title:
                        st.image(generate_thumbnail(step["description"]), caption="Generated Thumbnail")
                    elif "schedule" in title:
                        st.success(schedule_post(step["description"]))
                    else:
                        st.info("This step does not have a handler yet.")

# ----------------------------
# Studio Section Placeholder
# ----------------------------
elif section == "🎨 Editing Studio":
    st.markdown("## 🎨 Editing Studio")
    st.info("Auri's content editor is coming soon. This will be your visual workspace for posts and videos.")

# ----------------------------
# Schedule Section Placeholder
# ----------------------------
elif section == "🗖️ Posting & Scheduling":
    st.markdown("## 🗖️ Posting & Scheduling")
    st.info("Here you’ll be able to plan and schedule your social media content visually.")

# ----------------------------
# Analytics Section Placeholder
# ----------------------------
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance here in beautiful charts and reports.")