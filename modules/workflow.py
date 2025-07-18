from ideation.generator import generate_ideas, is_idea_or_repurpose_step
from modules.feedback import show_feedback_controls
from modules.script import generate_script_step_instruction
from modules.video import detect_video_ideas, analyze_script, determine_workflow, clean_label
from modules.tts import generate_voiceover_fallback as generate_voiceover_coqui
import re
import streamlit as st

def handle_step_execution(idx, step, input_val, uploaded_file, full_prompt):
    step_key = f"step_{idx}"
    title = step["title"].lower()

    if idx == 1 and is_idea_or_repurpose_step(step["title"], step["auri"]):
        ideas = generate_ideas(full_prompt, input_val)
        result = "\n".join(ideas)
        # ✅ Save the result so it re-renders on rerun
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result

        for i, idea in enumerate(ideas, 1):
            clean_idea = re.sub(r"\[.*?\]", "", idea).strip()
            st.markdown(f"💡 **Idea {i}:** {clean_idea}")
        return

    elif "script" in title:
        from modules.script import generate_script
        from modules.video import analyze_script, plan_footage

        tone = st.selectbox(
            "🎭 Select a tone",
            ["Informative", "Funny", "Shocking"],
            key=f"tone_{idx}"
        )
        platform = st.selectbox(
            "📱 Select platform",
            ["TikTok", "Instagram", "YouTube Shorts"],
            key=f"platform_{idx}"
        )
        prev_step_key = f"step_{idx-1}"
        prev_output = st.session_state["auri_context"]["step_outputs"].get(prev_step_key, "")
        user_instruction = step["user"]

        # Generate script text
        result = generate_script(
            goal=full_prompt,
            user_input=input_val,
            previous_output=prev_output,
            user_instruction=user_instruction,
            platform=platform,
            tone=tone
        )

        # ✅ Save script output so it's always visible
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result

        # Analyze script into structured scene data
        parsed_script = analyze_script(result)
        
        for scene in parsed_script.get("scenes", []):
            if scene["camera"]:
                scene["camera"] = re.sub(r"^Camera direction:\s*", "", scene["camera"], flags=re.I).strip('" ')
            if scene["lighting"]:
                scene["lighting"] = re.sub(r"^Lighting suggestion:\s*", "", scene["lighting"], flags=re.I).strip('" ')
            if scene["music"]:
                scene["music"] = re.sub(r"^Music style suggestion:\s*", "", scene["music"], flags=re.I).strip('" ')
            if scene["transition"]:
                scene["transition"] = re.sub(r"^Transition:\s*", "", scene["transition"], flags=re.I).strip('" ')
            if scene["onscreen_text"]:
                scene["onscreen_text"] = re.sub(r"^On-screen text:\s*", "", scene["onscreen_text"], flags=re.I).strip('" ')

        st.session_state["auri_context"]["parsed_script"] = parsed_script

        # Plan footage based on scenes
        planned_footage = plan_footage(parsed_script.get("scenes", []))

        # Clean visuals
        for item in planned_footage:
            if item["visual"]:
                item["visual"] = clean_label(item["visual"], "Camera direction:")

        st.session_state["auri_context"]["planned_footage"] = planned_footage

        # Detect workflow needs
        workflow = determine_workflow(result)
        st.session_state["auri_context"]["video_workflow"] = workflow

        # Insert video steps if needed
        if workflow["needs_video"]:
            video_steps = [
                {
                    "title": "Generate Voiceover",
                    "auri": "I will create a voiceover narration for your video scenes.",
                    "user": "Optionally upload a sample of your voice (WAV/MP3) or confirm using AI voice."
                },
                {
                    "title": "Assemble Video",
                    "auri": "I will combine your footage, voiceover, and on-screen text into a complete video.",
                    "user": "Review the final video and confirm if you'd like any edits."
                }
            ]

            insertion_index = idx
            st.session_state["auri_steps"] = (
                st.session_state["auri_steps"][:insertion_index]
                + video_steps
                + st.session_state["auri_steps"][insertion_index:]
            )

            # ✅ Rerun to show new steps
            st.rerun()

            return

    elif "voiceover" in title:
        from modules.tts import generate_voiceover_coqui, generate_voiceover_elevenlabs

        parsed_script = st.session_state["auri_context"].get("parsed_script")
        if not parsed_script:
            st.error("❌ No parsed script found. Please generate a script first.")
            return

        # Let the user choose TTS engine
        tts_engine = st.radio(
            "🎤 Select TTS Engine",
            ["Coqui TTS (local)", "ElevenLabs (cloud)"],
            key=f"tts_engine_{idx}"
        )

        if tts_engine == "ElevenLabs (cloud)":
            voice_id = st.text_input(
                "🔑 Enter your ElevenLabs voice_id",
                placeholder="e.g., abc123..."
            )
            api_key = st.text_input(
                "🔑 Enter your ElevenLabs API key",
                type="password"
            )

        # Generate button
        if st.button("🎙️ Generate Voiceovers"):
            audio_files = []
            for scene_idx, scene in enumerate(parsed_script["scenes"]):
                narration_text = scene["text"]
                if not narration_text.strip():
                    continue

                output_path = f"voiceover_scene_{scene_idx}.wav"

                if tts_engine == "Coqui TTS (local)":
                    generate_voiceover_coqui(narration_text, output_path)
                else:
                    if not voice_id or not api_key:
                        st.error("❌ Please enter your ElevenLabs API key and voice_id.")
                        return
                    generate_voiceover_elevenlabs(api_key, voice_id, narration_text, output_path)

                st.audio(output_path)
                audio_files.append(output_path)

            st.success(f"✅ Generated {len(audio_files)} voiceover files.")
            # Save the list in session state for later assembly
            st.session_state["auri_context"]["voiceover_files"] = audio_files

            return

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

            caption_result = generate_caption(
                goal=full_prompt,
                platform=platform,
                tone=tone,
                idea=idea,
                script=script,
                openai_key=st.secrets["openai"]["api_key"]
            )
            st.markdown("#### ✨ Suggested Caption")
            st.code(caption_result, language="markdown")
            captions.append(caption_result)

            hashtag_result = generate_hashtags(
                goal=full_prompt,
                idea=idea,
                script=script,
                platform=platform,
                openai_key=st.secrets["openai"]["api_key"]
            )
            st.markdown("#### 🏷️ Hashtag Suggestions")
            st.markdown(hashtag_result)
            hashtags.append(hashtag_result)

            combined_results.append(f"✨ Caption:\n{caption_result}\n\n🔖 Hashtags:\n{hashtag_result}")

        result = "\n\n---\n\n".join(combined_results)

        # ✅ Save
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result

        return

    elif "thumbnail" in title or "image" in title:
        from modules.thumbnail import generate_thumbnail
        result = generate_thumbnail(input_val or full_prompt)
        st.image(result, caption="Generated Thumbnail")

        # ✅ Save
        st.session_state["executed_steps"][step_key] = "Thumbnail generated."
        st.session_state["auri_context"]["step_outputs"][step_key] = "Thumbnail generated."
        return

    elif "schedule" in title or "post" in title:
        from modules.scheduler import schedule_post
        result = schedule_post(input_val or full_prompt)
        st.success(result)

        # ✅ Save
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    elif "upload" in title:
        result = f"📤 File received: {uploaded_file.name}" if uploaded_file else "No file uploaded"
        st.success(result)

        # ✅ Save
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    else:
        result = "✅ Step complete — no handler yet."
        st.info(result)

        # ✅ Save
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return