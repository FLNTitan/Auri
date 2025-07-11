import streamlit as st
from ideation.generator import generate_ideas, is_idea_or_repurpose_step
from modules.feedback import show_feedback_controls
from modules.script import generate_script_step_instruction
from modules.video import detect_video_ideas, analyze_script, determine_workflow, build_assembly_plan
from modules.workflow import handle_step_execution
from openai import OpenAI
import re
from PIL import Image

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
        
        Start by determining if the user is trying to repurpose existing content (e.g. tweets, blogs, captions, videos), or create something from scratch.

        Once you have determined if the user is trying to repurpose existing content or generate new ideas:
        - Do **not** include vague or redundant steps like “Content Review” or “Reels Concept.”
        - Start directly from either:
        1. Repurposing the user’s content (like tweets, blogs, past posts etc ...) into ideas, or
        2. Generating new ideas from scratch if no input is provided or the goal requested does not require the user to share any media with you. Be flexible and match the user's prompt.
        
        - ❌ Do not include generic, vague steps like “Develop Concept” or “Review Content” unless they serve a clear function and require user input.
        - Be aware of what is the logical order to execute the steps and suggest them in order (e.g. do not include a "Generate Ideas" step after "Scripting" step)
        - If the user is repurposing content (e.g. tweets), you must not suggest generating new ideas afterward.


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

        # Check if Step 1 output includes video ideas
        prev_step_outputs = st.session_state["auri_context"].get("step_outputs", {})
        step_1_output = prev_step_outputs.get("step_1", "")

        if isinstance(step_1_output, str):
            step_1_lines = [line.strip() for line in step_1_output.split("\n") if line.strip()]
        else:
            step_1_lines = step_1_output

        should_force_script = detect_video_ideas(step_1_lines)

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
            # --- Auto-insert Script Writing step if needed ---
            step_titles = [s["title"].lower() for s in parsed_steps]
            if should_force_script and not any("script" in title for title in step_titles):
                # Pick a video idea to describe in the prompt:
                idea_output = st.session_state["auri_context"]["step_outputs"].get("step_1", "")
                video_idea = next((line for line in idea_output.split("\n") if any(x in line.lower() for x in ["reel", "short", "video"])), "")
                dynamic_script_step = generate_script_step_instruction(client, idea_text=video_idea)
                if dynamic_script_step:
                    parsed_steps.insert(1, dynamic_script_step)
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

                # Save step input and title
                st.session_state["auri_context"]["step_inputs"][step_key] = input_val
                st.session_state["auri_context"]["step_titles"][step_key] = step["title"]

                if step_key in st.session_state["executed_steps"]:
                    result = st.session_state["executed_steps"][step_key]

                    if isinstance(result, str) and result.strip():
                        st.markdown("#### ✅ Auri’s Output")
                        st.markdown(result)

                        if (
                            step["title"].lower().startswith("script")
                            and "parsed_script" in st.session_state["auri_context"]
                            and "planned_footage" in st.session_state["auri_context"]
                        ):
                            with st.expander("🎞️ Click to Review and Upload Scene Footage"):
                                # Initialize dict if missing
                                if "scene_selections" not in st.session_state["auri_context"]:
                                    st.session_state["auri_context"]["scene_selections"] = {}

                                for scene in st.session_state["auri_context"]["planned_footage"]:
                                    scene_key = f"scene_{scene['scene_index']}"
                                    selection = st.session_state["auri_context"]["scene_selections"].get(scene_key, {})

                                    st.markdown(f"#### 🎬 Scene {scene['scene_index'] + 1}")
                                    st.write(f"- 🎥 **Visual**: {scene['visual']}")
                                    st.write(f"- 🖼 **On-screen Text**: {scene['onscreen_text']}")
                                    st.write(f"- 🎶 **Music**: {scene['music']}")
                                    st.write(f"- 🔄 **Transition**: {scene['transition']}")

                                    # Persisted checkbox
                                    use_stock = st.checkbox(
                                        "✅ Use Stock Footage",
                                        value=selection.get("use_stock", False),
                                        key=f"use_stock_{scene_key}"
                                    )

                                    # Persisted uploader
                                    uploaded = st.file_uploader(
                                        "📤 Upload your clip",
                                        key=f"upload_scene_{scene_key}"
                                    )

                                    # Save state
                                    st.session_state["auri_context"]["scene_selections"][scene_key] = {
                                        "use_stock": use_stock,
                                        "filename": uploaded.name if uploaded else selection.get("filename")
                                    }

                                    # Display what the user has chosen
                                    if uploaded:
                                        st.success(f"✅ Uploaded: {uploaded.name}")
                                    elif use_stock:
                                        st.info("ℹ️ Using stock footage.")
                                    else:
                                        st.warning("⚠️ No footage selected yet.")

                                    st.markdown("---")
                                st.subheader("🎬 Final Assembly Plan")

                            assembly_plan = build_assembly_plan(
                                st.session_state["auri_context"]["planned_footage"],
                                st.session_state["auri_context"]["scene_selections"]
                            )

                            for item in assembly_plan:
                                st.markdown(f"""
                                    **Scene {item['scene_index'] + 1}**
                                    - ✅ Using: {"Stock Footage" if item['use_stock'] else "User Upload" if item['filename'] else "❌ Not selected"}
                                    - 🎥 Visual: {item['visual']}
                                    - 🖼 On-screen Text: {item['onscreen_text'] or "—"}
                                    - 🎶 Music: {item['music'] or "—"}
                                    - 🔄 Transition: {item['transition'] or "—"}
                                    """)
                                if not item["use_stock"] and not item["filename"]:
                                    st.error("⚠️ This scene is missing footage!")
                            st.markdown("---")

                            if st.button("🎥 Generate Final Video"):
                                st.session_state["auri_context"]["assembly_plan"] = assembly_plan
                                st.success("✅ Assembly plan saved! (Rendering logic not yet implemented.)")

                    show_feedback_controls(
                        step_key=step_key,
                        step_title=step["title"],
                        regenerate_callback=lambda user_feedback: st.warning(f"⚙️ Regeneration not yet implemented for Step {idx}."),
                        language=language
                    )

                elif input_ready and step_key not in st.session_state["executed_steps"] and st.button(f"▶ Run Step {idx}", key=f"run_step_{idx}"):
                    with st.spinner("Running..."):
                        handle_step_execution(idx, step, input_val, uploaded_file, full_prompt)
                        st.rerun()
                        # 🎯 Show debug info if available
            
            parsed_script = st.session_state["auri_context"].get("parsed_script")
            planned_footage = st.session_state["auri_context"].get("planned_footage")
            video_workflow = st.session_state["auri_context"].get("video_workflow")

            if parsed_script:
                st.subheader("🎬 Parsed Script Scenes")
                st.json(parsed_script)

            if planned_footage:
                st.subheader("📹 Planned Footage")
                st.json(planned_footage)

            if video_workflow:
                st.subheader("⚙️ Workflow Analysis")
                st.write(video_workflow)
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

    st.markdown("### 🖼️ Thumbnail Generator")

    # ----------------------------
    # 1️⃣ Retrieve previous outputs
    # ----------------------------
    step_outputs = st.session_state.get("auri_context", {}).get("step_outputs", {})
    default_title = (
        step_outputs.get("step_2", "").split("\n")[0]
        if step_outputs.get("step_2")
        else "Your Title Here"
    )
    default_subtitle = step_outputs.get("step_3", "") or ""

    platform = st.selectbox("📱 Select platform", ["YouTube", "TikTok", "Instagram", "LinkedIn"])
    style = st.selectbox(
        "🎨 Select style",
        ["Clean & Modern", "Bold & Dynamic", "Playful & Fun", "Minimalist & Elegant"]
    )
    custom_style = st.text_input(
        "✏️ (Optional) Describe any custom style instructions",
        placeholder="e.g. Add neon glow, use purple background"
    )

    # ----------------------------
    # 2️⃣ User Inputs
    # ----------------------------
    title = st.text_input("Thumbnail Title", value=default_title)
    subtitle = st.text_input("Thumbnail Subtitle", value=default_subtitle)

    uploaded_file = st.file_uploader("📤 Upload an image to use as a base")

    generate_ai = st.button("🎨 Generate AI Image")

    # Prepare variable to hold the base image path
    base_image_path = None

    # ----------------------------
    # 3️⃣ Handle AI Generation
    # ----------------------------
    if generate_ai:
        with st.spinner("Generating AI Image..."):
            from modules.thumbnail import generate_thumbnail_prompt, download_image

            script_text = step_outputs.get("step_2", "")
            hashtags = step_outputs.get("step_3", "")

            prompt = generate_thumbnail_prompt(
                script_text,
                hashtags,
                platform,
                style,
                custom_style
            )

            client = OpenAI(api_key=st.secrets["openai"]["api_key"])

            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            st.image(image_url, caption="AI Generated Thumbnail")
            download_image(image_url, "ai_thumbnail.jpg")
            base_image_path = "ai_thumbnail.jpg"

    # ----------------------------
    # 4️⃣ Final Thumbnail Creation
    # ----------------------------
    if st.button("✅ Generate Final Thumbnail"):
        from modules.thumbnail_config import THUMBNAIL_STYLES
        from modules.thumbnail import create_thumbnail

        if uploaded_file:
            image = Image.open(uploaded_file)
            # Convert RGBA to RGB if needed
            if image.mode == "RGBA":
                image = image.convert("RGB")    

            image.save("uploaded_image.jpg")
            base_image_path = "uploaded_image.jpg"

        if not base_image_path:
            st.error("Please upload an image or generate one first.")
        else:
            output_path = create_thumbnail(
                base_image_path,
                title,
                subtitle,
                config=THUMBNAIL_STYLES["default"],
                output_path="final_thumbnail.jpg"
            )
            st.image(output_path, caption="Your Thumbnail is Ready!")

            # Store metadata
            st.session_state["auri_context"]["step_outputs"]["thumbnail"] = {
                "source": "uploaded" if uploaded_file else "AI",
                "title": title,
                "subtitle": subtitle,
                "script_used": script_text,
                "hashtags_used": hashtags
            }
elif section == "🗖️ Posting & Scheduling":
    st.markdown("## 🗖️ Posting & Scheduling")
    st.info("Plan and schedule your content visually.")
elif section == "📊 Analytics":
    st.markdown("## 📊 Performance Analytics")
    st.info("Auri will track and summarize your content performance.")
