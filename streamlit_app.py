import streamlit as st
from ideation.generator import generate_ideas
from openai import OpenAI
import re

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
# Hero Section
# ----------------------------
st.markdown("""
    <div style='text-align: center; margin-top: 2rem; margin-bottom: 1rem;'>
        <h1 style='color: #6C63FF; font-size: 2.8rem;'>✨ Auri: Your AI Social Media Copilot</h1>
        <p style='font-size: 1.1rem; color: #1F2937;'>Plan, create, and publish your content with intelligent guidance and powerful creative tools 🚀</p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------
# Content Ideas Workflow
# ----------------------------
if section == "🧠 Content Ideas":
    st.markdown("## 🧠 Content Ideation")
    st.markdown("Kickstart your workflow with a smart recipe or describe your goal in plain English.")

    with st.expander("🌍 Quick Start Recipes"):
        cols = st.columns(3)
        if cols[0].button("📈 Viral TikTok Sprint"):
            st.session_state["prompt"] = "Plan 3 viral TikTok posts with script, thumbnail, and schedule"
        if cols[1].button("🎨 Weekend Reel Builder"):
            st.session_state["prompt"] = "Create 2 weekend Instagram Reels with catchy hooks and music"
        if cols[2].button("🎬 YouTube-to-Short"):
            st.session_state["prompt"] = "Repurpose latest YouTube video into 3 Shorts with new captions"

    user_prompt = st.text_input("Or describe your goal...", placeholder="e.g. Turn my last 2 tweets into a carousel and reel")

    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    if user_prompt and user_prompt != st.session_state.get("prompt", ""):
        st.session_state["prompt"] = user_prompt

    full_prompt = st.session_state.get("prompt", "").strip()

    if not full_prompt:
        st.info("👆 Start by selecting a quick recipe or describing your goal above.")
    else:
        st.markdown(f"#### 💡 Auri is preparing your flow ####")

        workflow_prompt = f"""
            You are Auri, an AI social media copilot that guides content creators through a complete workflow using natural language.

            The user's goal is: "{full_prompt}"

            Break this goal into 3–6 steps required to complete it.

            Each step must include:
            1. A clear step title (e.g. "Generate Ideas", "Script Writing", "Upload Media")
            2. Two subpoints:
            - "I will..." → What Auri will autonomously handle in this step.
            - "To do that, I’ll need you to..." → Ask the user for **only** what Auri cannot do. Phrase this as a clear instruction or question.

            ⚠️ Be smart: Do not ask the user to help with tasks Auri can already do or will be able to do soon.

            ---

            ### ✅ Auri’s CURRENT capabilities:
            - Understand free-text goals and translate them into structured workflows.
            - Generate content ideas and angles.
            - Write video or carousel scripts.
            - Suggest captions, hooks, and hashtags.
            - Generate thumbnails or cover image prompts.
            - Create content plans and posting schedules.
            - Decide optimal posting times.
            - Accept user inputs (text or uploads) when required.

            ### 🔜 Auri’s FUTURE capabilities:
            - Fully automate video editing based on scripts or uploaded footage.
            - Track engagement and performance of posts.
            - Analyze content to recommend changes or improvements.
            - Automatically post and schedule content via platform integrations.
            - Manage cross-platform content pipelines.
            - Extract and transform data from user's past posts or analytics.

            ---

            ### ⚠️ You must:
            - NEVER ask the user to do things Auri already handles.
            - ONLY request what’s absolutely needed from the user to complete the task.
            - Be concise, helpful, and confident.

            ---

            ### Format (strict):
            1. Step Title | I will... | To do that, I’ll need you to...

            No introductions. No summaries.
            """


        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": workflow_prompt}],
            temperature=0.5,
        )

        step_lines = response.choices[0].message.content.strip().split("\n")

        steps = []
        for line in step_lines:
            match = re.match(r"^\s*\d+\.\s*(.*?)\s+\|\s+(I will.*?)\s+\|\s+(To do that.*?)$", line.strip(), re.IGNORECASE)
            if match:
                steps.append({
                    "title": match.group(1).strip(),
                    "auri": match.group(2).strip(),
                    "user": match.group(3).strip()
                })

        if steps:
            if "executed_steps" not in st.session_state:
                st.session_state["executed_steps"] = {}

            st.markdown("---")
            st.markdown("### ✅ Here's how we'll make it happen:")

            for idx, step in enumerate(steps, 1):
                step_key = f"step_{idx}"
                st.markdown(f"**Step {idx}: {step['title']}**")
                st.caption(f"🤖 {step['auri']}")
                st.caption(f"📥 {step['user']}")

                input_val = None
                uploaded_file = None
                input_ready = True

                if "upload" in step["user"].lower():
                    uploaded_file = st.file_uploader("📤 Upload media", key=f"upload_{idx}")
                    input_ready = uploaded_file is not None
                    input_val = uploaded_file.name if uploaded_file else None
                elif any(word in step["user"].lower() for word in ["write", "text", "type", "share"]):
                    input_val = st.text_area("✍️ Enter your input", key=f"text_{idx}")
                    input_ready = bool(input_val)

                if step_key in st.session_state["executed_steps"]:
                    result = st.session_state["executed_steps"][step_key]
                    st.success("✅ Step completed.")
                    st.caption(f"📝 Result: {result}")
                elif input_ready and st.button(f"▶ Run Step {idx}", key=f"run_step_{idx}"):
                    with st.spinner("Running..."):
                        result = None
                        title = step["title"].lower()

                        if "idea" in title:
                            ideas = generate_ideas(full_prompt)
                            result = "\n".join([f"💡 {i+1}. {idea}" for i, idea in enumerate(ideas)])
                            for line in result.split("\n"):
                                st.markdown(line)
                        elif "script" in title:
                            from modules.script import generate_script

                            # User selects tone/platform per script step
                            tone = st.selectbox("🎭 Select a tone", ["Informative", "Funny", "Shocking"], key=f"tone_{idx}")
                            platform = st.selectbox("📱 Select platform", ["TikTok", "Instagram", "YouTube Shorts"], key=f"platform_{idx}")

                            # Generate script based on user input or full prompt
                            result = generate_script(input_val or full_prompt, platform=platform, tone=tone)

                            # Display output nicely
                            st.code(result, language="markdown")

                            st.success(result)
                        elif "thumbnail" in title or "image" in title:
                            from modules.thumbnail import generate_thumbnail
                            result = generate_thumbnail(input_val or full_prompt)
                            st.image(result, caption="Generated Thumbnail")
                        elif "schedule" in title or "post" in title:
                            from modules.scheduler import schedule_post
                            result = schedule_post(input_val or full_prompt)
                            st.success(result)
                        elif "upload" in title:
                            result = f"📤 File received: {uploaded_file.name}" if uploaded_file else "No file uploaded"
                            st.success(result)
                        else:
                            result = "✅ Step complete — no handler yet."
                            st.info(result)

                        st.session_state["executed_steps"][step_key] = result

                        if idx < len(steps):
                            st.markdown("---")
                            st.info(f"👉 Ready to continue with **Step {idx+1}**: {steps[idx]['title']}?")

# ----------------------------
# Other Sections
# ----------------------------
elif section == "🎨 Editing Studio":
    st.markdown("## 🎨 Editing Studio")
    st.info("Auri's content editor is coming soon.")

elif section == "🗖️ Posting & Scheduling":
    st.markdown("## 🗖️ Posting & Scheduling")
    st.info("Plan and schedule your content visually.")

elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance.")
