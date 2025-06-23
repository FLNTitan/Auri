import streamlit as st
from ideation.generator import generate_ideas
from modules.feedback import show_feedback_controls
from openai import OpenAI
import re

TEXT = {
    "English": {
        "nav": ["🧠 Content Ideas", "🎨 Editing Studio", "🗖️ Posting & Scheduling", "📊 Analytics"],
        "title": "✨ Auri: Your AI Social Media Copilot",
        "subtitle": "Plan, create, and publish your content with intelligent guidance and powerful creative tools 🚀",
        "start": "👆 Start by selecting a quick recipe or describing your goal above.",
        "input_label": "✍️ Enter your input",
        "upload_label": "📤 Upload media",
        "step_label": "👉 Ready to continue with Step",
        "missing_prompt": "🧩 Auri can help you even more! Would you also like help with:",
        "show_more": "➕ Yes, show additional steps",
        "bonus_title": "🔄 Additional Auri Capabilities You Haven’t Used Yet:"
    },
    "עברית": {
        "nav": ["🧠 רעיונות לתוכן", "🎨 סטודיו לעריכה", "🗖️ תזמון פרסומים", "📊 ניתוחים"],
        "title": "✨ Auri: העוזר החכם שלך ליצירת תוכן",
        "subtitle": "תכנן, צור ופרסם תוכן בצורה חכמה ומהירה עם Auri 🚀",
        "start": "👆 בחר תבנית התחלה מהירה או כתוב מה אתה רוצה ש-Auri יעשה בשבילך.",
        "input_label": "✍️ מה תרצה להוסיף כאן?",
        "upload_label": "📤 העלה קובץ או מדיה רלוונטית",
        "step_label": "👉 נמשיך לשלב הבא: שלב",
        "missing_prompt": "🧩 רוצה ש-Auri יעזור גם עם:",
        "show_more": "➕ כן, תראה לי עוד שלבים",
        "bonus_title": "🔄 יכולות נוספות של Auri שטרם נוצלו:"
    }
}


st.set_page_config(
    page_title="Auri | Your AI Social Media Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "auri_language" not in st.session_state:
    st.session_state["auri_language"] = "English"

language = st.session_state["auri_language"]

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

if st.session_state["auri_language"] == "עברית":
    st.markdown("""
    <style>
    html[dir="ltr"] {
        direction: rtl;
    }
    .stMarkdown, .css-1kyxreq, .css-10trblm {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)


with st.sidebar:
    logo_col = st.columns([1, 2, 1])[1]
    with logo_col:
        st.image("auri_logo_circular.png", width=120)

    # Language selector
    language = st.selectbox(
        "🌍 Choose language",
        ["English", "עברית"],
        index=0 if st.session_state["auri_language"] == "English" else 1
    )
    st.session_state["auri_language"] = language

    st.markdown("## 🧽 Navigation")
    section = st.radio(
        "Jump to",
        TEXT[language]["nav"]
    )

st.markdown(f"""
    <div style='text-align: center; margin-top: 2rem; margin-bottom: 1rem;'>
        <h1 style='color: #6C63FF; font-size: 2.8rem;'>{TEXT[language]["title"]}</h1>
        <p style='font-size: 1.1rem; color: #1F2937;'>{TEXT[language]["subtitle"]}</p>
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

        ✅ If the user’s request sounds narrow (e.g. only asking for ideas or a caption), fulfill that — but also suggest optional next steps Auri can help with, to complete the content creation pipeline.

        At the end of your response, do the following:

        - Check which of Auri’s capabilities were **not included** in the generated steps.
        - If relevant steps are missing based on the user’s goal, suggest them as a friendly follow-up:

        🧩 “Would you also like help with: [missing steps]?”

        Only suggest useful and missing ones. Do not repeat steps already included.

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


        if "auri_steps" not in st.session_state:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": workflow_prompt}],
                temperature=0.5,
            )
            step_lines = response.choices[0].message.content.strip().split("\n")
            parsed_steps = []
            for line in step_lines:
                match = re.match(r"^\s*\d+\.\s*(.*?)\s+\|\s+(I will.*?)\s+\|\s+(To do that.*?)$", line.strip(), re.IGNORECASE)
                if match:
                    parsed_steps.append({
                        "title": match.group(1).strip(),
                        "auri": match.group(2).strip(),
                        "user": match.group(3).strip()
                    })
            st.session_state["auri_steps"] = parsed_steps

            # Track which capabilities were included
            included_titles = [step["title"].lower() for step in parsed_steps]
            auri_capabilities = {
                "ideas": "Generate Ideas",
                "script": "Script Writing",
                "caption": "Suggest Captions and Hashtags",
                "thumbnail": "Generate Thumbnails or Cover Images",
                "plan": "Create Content Plans",
                "schedule": "Schedule Posts"
            }
            missing_steps = [
                readable for keyword, readable in auri_capabilities.items()
                if not any(keyword in title for title in included_titles)
            ]
            st.session_state["auri_missing_suggestions"] = missing_steps

        steps = st.session_state["auri_steps"]

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

                st.session_state["auri_context"]["step_inputs"][step_key] = input_val
                st.session_state["auri_context"]["step_titles"][step_key] = step["title"]

                # === Step already executed ===
                if step_key in st.session_state["executed_steps"]:
                    result = st.session_state["executed_steps"][step_key]
                    st.success("✅ Step completed.")

                    # Output handling
                    if "script" in step["title"].lower():
                        st.code(result, language="markdown")
                    elif "idea" in step["title"].lower():
                        for idea in result.split("\n"):
                            st.markdown(f"- {idea.strip()}")
                    elif "caption" in step["title"].lower() or "hashtag" in step["title"].lower():
                        st.markdown(result)
                    elif "thumbnail" in step["title"].lower():
                        st.image(result, caption="Generated Thumbnail")
                    else:
                        st.markdown(result)

                    # Feedback
                    def regenerate_wrapper(user_feedback):
                        step_title = step["title"].lower()
                        if "idea" in step_title:
                            from ideation.generator import generate_ideas
                            regenerated = generate_ideas(full_prompt, user_feedback)
                            display = "\n".join(regenerated)
                            for idea in regenerated:
                                st.markdown(f"- {idea.strip()}")
                            st.session_state["executed_steps"][step_key] = display
                            st.session_state["auri_context"]["step_outputs"][step_key] = display

                        elif "script" in step_title:
                            from modules.script import generate_script
                            tone = st.session_state.get(f"tone_{idx}", "Informative")
                            platform = st.session_state.get(f"platform_{idx}", "TikTok")
                            prev_step_key = f"step_{idx-1}"
                            prev_output = st.session_state["auri_context"]["step_outputs"].get(prev_step_key, "")
                            regenerated = generate_script(
                                goal=full_prompt,
                                user_input=input_val,
                                previous_output=prev_output,
                                user_instruction=user_feedback,
                                platform=platform,
                                tone=tone
                            )
                            st.code(regenerated)
                            st.session_state["executed_steps"][step_key] = regenerated
                            st.session_state["auri_context"]["step_outputs"][step_key] = regenerated

                        # Add more step types as needed...

                    from modules.feedback import show_feedback_controls
                    show_feedback_controls(
                        step_key=step_key,
                        step_title=step["title"],
                        regenerate_callback=regenerate_wrapper,
                        language=language,
                        platform="Web"
                    )

                # === Step not yet executed ===
                elif input_ready and st.button(f"▶ Run Step {idx}", key=f"run_step_{idx}"):
                    with st.spinner("Running..."):
                        result = None
                        title = step["title"].lower()

                        if "idea" in title:
                            ideas = generate_ideas(full_prompt, input_val)
                            result = "\n".join(ideas)
                            for idea in ideas:
                                st.markdown(f"- {idea.strip()}")

                        elif "script" in title:
                            from modules.script import generate_script
                            tone = st.selectbox("🎭 Select a tone", ["Informative", "Funny", "Shocking"], key=f"tone_{idx}")
                            platform = st.selectbox("📱 Select platform", ["TikTok", "Instagram", "YouTube Shorts"], key=f"platform_{idx}")
                            prev_step_key = f"step_{idx-1}"
                            prev_output = st.session_state["auri_context"]["step_outputs"].get(prev_step_key, "")
                            user_instruction = step["user"]
                            result = generate_script(
                                goal=full_prompt,
                                user_input=input_val,
                                previous_output=prev_output,
                                user_instruction=user_instruction,
                                platform=platform,
                                tone=tone
                            )
                            st.code(result, language="markdown")

                        elif "caption" in title or "hashtag" in title:
                            from modules.captions import generate_caption
                            from modules.hashtags import generate_hashtags
                            idea_list = st.session_state["auri_context"]["step_outputs"].get("step_1", [])
                            script_list = st.session_state["auri_context"]["step_outputs"].get("step_2", [])
                            if isinstance(idea_list, str):
                                idea_list = [line for line in idea_list.split("\n") if line.strip()]
                            if isinstance(script_list, str):
                                script_list = [line for line in script_list.split("\n") if line.strip()]
                            platform = st.selectbox("📱 Select platform", ["TikTok", "Instagram", "YouTube Shorts"], key=f"platform_caption_{idx}")
                            tone = st.selectbox("🎭 Select tone", ["Funny", "Inspiring", "Bold", "Shocking"], key=f"tone_caption_{idx}")
                            combined_results = []
                            captions = []
                            hashtags = []
                            for i, (idea, script) in enumerate(zip(idea_list, script_list), start=1):
                                st.markdown(f"### 📝 Post {i}")
                                cleaned_idea = idea.split(".", 1)[-1].strip()
                                st.markdown(f"<div style='font-size: 1.05rem; color: #1F2937;'>{cleaned_idea}</div>", unsafe_allow_html=True)
                                caption_result = generate_caption(goal=full_prompt, platform=platform, tone=tone, idea=idea, script=script, openai_key=st.secrets["openai"]["api_key"])
                                st.markdown("#### ✨ Suggested Caption")
                                st.code(caption_result, language="markdown")
                                captions.append(caption_result)
                                hashtag_result = generate_hashtags(goal=full_prompt, idea=idea, script=script, platform=platform, openai_key=st.secrets["openai"]["api_key"])
                                st.markdown("#### 🏷️ Hashtag Suggestions")
                                st.markdown(hashtag_result)
                                hashtags.append(hashtag_result)
                                combined_results.append(f"✨ Caption:\n{caption_result}\n\n🔖 Hashtags:\n{hashtag_result}")
                            st.session_state["auri_context"]["captions"] = captions
                            st.session_state["auri_context"]["hashtags"] = hashtags
                            result = "\n\n---\n\n".join(combined_results)

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

                        
            # Show suggestion prompt after all steps are displayed
            if st.session_state.get("auri_missing_suggestions"):
                suggestions = st.session_state["auri_missing_suggestions"]

                if "expand_extra_steps" not in st.session_state:
                    st.session_state["expand_extra_steps"] = False

                st.markdown("---")
                st.info(f"🧩 Auri can help you even more! Would you also like help with: {', '.join(suggestions)}?")

                if st.button("➕ Yes, show additional steps", key="extra_steps_button"):
                    st.session_state["expand_extra_steps"] = True

                if st.session_state["expand_extra_steps"]:
                    st.markdown("### 🔄 Additional Auri Capabilities You Haven’t Used Yet:")
                    for item in suggestions:
                        st.markdown(f"- ✅ **{item}** – available in upcoming versions or can be triggered manually.")


elif section == "🎨 Editing Studio":
    st.markdown("## 🎨 Editing Studio")
    st.info("Auri's content editor is coming soon.")
elif section == "🗖️ Posting & Scheduling":
    st.markdown("## 🗖️ Posting & Scheduling")
    st.info("Plan and schedule your content visually.")
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance.")
