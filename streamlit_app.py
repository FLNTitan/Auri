import streamlit as st
from ideation.generator import generate_ideas
from openai import OpenAI
import re

st.set_page_config(
    page_title="Auri | Your AI Social Media Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

with st.sidebar:
    logo_col = st.columns([1, 2, 1])[1]
    with logo_col:
        st.image("auri_logo_circular.png", width=120)

    st.markdown("## 🧽 Navigation")
    section = st.radio(
        "Jump to",
        ["🧠 Content Ideas", "🎨 Editing Studio", "🗖️ Posting & Scheduling", "📊 Analytics"]
    )

st.markdown("""
    <div style='text-align: center; margin-top: 2rem; margin-bottom: 1rem;'>
        <h1 style='color: #6C63FF; font-size: 2.8rem;'>✨ Auri: Your AI Social Media Copilot</h1>
        <p style='font-size: 1.1rem; color: #1F2937;'>Plan, create, and publish your content with intelligent guidance and powerful creative tools 🚀</p>
    </div>
""", unsafe_allow_html=True)

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

        if "auri_context" not in st.session_state:
            st.session_state["auri_context"] = {
                "goal": full_prompt,
                "step_inputs": {},
                "step_outputs": {},
                "step_titles": {}
            }

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"You are Auri, an AI social media copilot... (same prompt as before)"}],
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
                elif any(word in step["user"].lower() for word in ["write", "text", "type", "share", "confirm", "describe", "tell", "message", "highlight"]):
                    input_val = st.text_area("✍️ Enter your input", key=f"text_{idx}")
                    input_ready = bool(input_val)
                else:
                    input_val = st.text_area("✍️ (Optional) Enter any input Auri might need", key=f"text_{idx}")
                    input_ready = True

                # Save step input and title
                st.session_state["auri_context"]["step_inputs"][step_key] = input_val
                st.session_state["auri_context"]["step_titles"][step_key] = step["title"]

                if step_key in st.session_state["executed_steps"]:
                    result = st.session_state["executed_steps"][step_key]
                    st.success("✅ Step completed.")
                    st.caption(f"📝 Result: {result}")
                elif input_ready and st.button(f"▶ Run Step {idx}", key=f"run_step_{idx}"):
                    with st.spinner("Running..."):
                        result = None
                        title = step["title"].lower()

                        if "idea" in title:
                            ideas = generate_ideas(full_prompt, input_val)
                            result = "\n".join([f"💡 {i+1}. {idea}" for i, idea in enumerate(ideas)])
                            for line in result.split("\n"):
                                st.markdown(line)
                        elif "script" in title:
                            from modules.script import generate_script
                            tone = st.selectbox("🎭 Select a tone", ["Informative", "Funny", "Shocking"], key=f"tone_{idx}")
                            platform = st.selectbox("📱 Select platform", ["TikTok", "Instagram", "YouTube Shorts"], key=f"platform_{idx}")

                            prev_step_key = f"step_{idx-1}"
                            prev_output = st.session_state["auri_context"]["step_outputs"].get(prev_step_key, "")
                            result = generate_script(
                                goal=full_prompt,
                                user_input=input_val,
                                previous_output=prev_output,
                                platform=platform,
                                tone=tone
                            )
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
                        st.session_state["auri_context"]["step_outputs"][step_key] = result

                        if idx < len(steps):
                            st.markdown("---")
                            st.info(f"👉 Ready to continue with **Step {idx+1}**: {steps[idx]['title']}?")

elif section == "🎨 Editing Studio":
    st.markdown("## 🎨 Editing Studio")
    st.info("Auri's content editor is coming soon.")
elif section == "🗖️ Posting & Scheduling":
    st.markdown("## 🗖️ Posting & Scheduling")
    st.info("Plan and schedule your content visually.")
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance.")
