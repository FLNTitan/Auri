import streamlit as st
from ideation.generator import generate_ideas
from modules.script import generate_script
from modules.thumbnail import generate_thumbnail
from modules.scheduler import schedule_post
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

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
        ["🧠 Content Ideas", "🎨 Editing Studio", "🖖️ Posting & Scheduling", "📊 Analytics"]
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
    st.markdown("Kickstart your workflow with a smart recipe or describe your goal in plain English.")

    if "prompt" not in st.session_state:
        st.session_state["prompt"] = ""

    with st.expander("🌍 Quick Start Recipes"):
        cols = st.columns(3)
        if cols[0].button("\U0001f4c8 Viral TikTok Sprint"):
            st.session_state["prompt"] = "Plan 3 viral TikTok posts with script, thumbnail, and schedule"
            st.rerun()
        if cols[1].button("\U0001f3a8 Weekend Reel Builder"):
            st.session_state["prompt"] = "Create 2 weekend Instagram Reels with catchy hooks and music"
            st.rerun()
        if cols[2].button("\U0001f3a7 YouTube-to-Short"):
            st.session_state["prompt"] = "Repurpose latest YouTube video into 3 Shorts with new captions"
            st.rerun()

    user_input = st.text_input(
        "Or describe your goal...",
        value=st.session_state["prompt"],
        placeholder="e.g. Turn my last 2 tweets into a carousel and reel"
    )

    if user_input and user_input != st.session_state["prompt"]:
        st.session_state["prompt"] = user_input
        st.rerun()

    if st.session_state["prompt"]:
        st.markdown(f"#### 💡 Auri is preparing your workflow for: _{st.session_state['prompt']}_")

        if any(keyword in st.session_state["prompt"].lower() for keyword in ["ideas", "suggest", "give me", "what are"]):
            ideas = generate_ideas(st.session_state["prompt"])
            st.markdown("### 🌟 Content Ideas")
            for idx, idea in enumerate(ideas, 1):
                idea_clean = idea.lstrip("0123456789.- ").strip()
                st.markdown(f"<div class='idea-card'>🔹 <strong>Idea {idx}:</strong> {idea_clean}</div>", unsafe_allow_html=True)
            base_task = ideas[0]
        else:
            base_task = st.session_state["prompt"]

        workflow_prompt = f"""
Act as an AI content operations assistant.
Given the user goal: \"{st.session_state['prompt']}\" and task: \"{base_task}\",
break down the production process into 3–5 steps.
Include any dependencies (e.g. if you need the user to upload media).
Return as a numbered list.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": workflow_prompt}],
            temperature=0.7,
        )
        steps_raw = response.choices[0].message.content.split("\n")
        steps = [
            {"title": step.split(". ", 1)[-1].strip(), "description": ""} for step in steps_raw if step.strip()
        ]

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
                        st.success(generate_script(st.session_state["prompt"]))
                    elif "thumbnail" in title:
                        st.image(generate_thumbnail(st.session_state["prompt"]), caption="Generated Thumbnail")
                    elif "schedule" in title:
                        st.success(schedule_post(st.session_state["prompt"]))
                    elif "upload" in title:
                        st.warning("Please upload the required media to proceed.")
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
elif section == "🖖️ Posting & Scheduling":
    st.markdown("## 🖖️ Posting & Scheduling")
    st.info("Here you’ll be able to plan and schedule your social media content visually.")

# ----------------------------
# Analytics Section Placeholder
# ----------------------------
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance here in beautiful charts and reports.")
