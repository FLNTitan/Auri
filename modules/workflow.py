from ideation.generator import generate_ideas, is_idea_or_repurpose_step
from modules.feedback import show_feedback_controls
from modules.script import generate_script_step_instruction
from modules.video import detect_video_ideas, analyze_script, determine_workflow, clean_label
from modules.tts import generate_voiceover_fallback
import re
import streamlit as st

def handle_step_execution(idx, step, input_val, uploaded_file, full_prompt):
    step_key = f"step_{idx}"
    title = step["title"].lower()

    def handle_idea_step():
        ideas = generate_ideas(full_prompt, input_val)
        result = "\n".join(ideas)
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        for i, idea in enumerate(ideas, 1):
            clean_idea = re.sub(r"\[.*?\]", "", idea).strip()
            st.markdown(f"💡 **Idea {i}:** {clean_idea}")
        return

    def handle_script_step():
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
        result = generate_script(
            goal=full_prompt,
            user_input=input_val,
            previous_output=prev_output,
            user_instruction=user_instruction,
            platform=platform,
            tone=tone
        )
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
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
        planned_footage = plan_footage(parsed_script.get("scenes", []))
        for item in planned_footage:
            if item["visual"]:
                item["visual"] = clean_label(item["visual"], "Camera direction:")
        st.session_state["auri_context"]["planned_footage"] = planned_footage
        workflow = determine_workflow(result)
        st.session_state["auri_context"]["video_workflow"] = workflow
        if workflow["needs_video"]:
            existing_titles = [s["title"].lower() for s in st.session_state["auri_steps"]]
            if not any("voiceover" in title for title in existing_titles):
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
                st.rerun()
        return

    def handle_voiceover_step():
        from modules.tts import generate_voiceover_fallback
        import os
        parsed_script = st.session_state["auri_context"].get("parsed_script")
        if not parsed_script:
            st.error("❌ No parsed script found. Please generate a script first.")
            return

        # Session state keys
        gen_key = f"voiceover_generated_{step_key}"
        approve_key = f"voiceover_approved_{step_key}"
        audio_files_key = f"voiceover_files_{step_key}"

        def do_generate():
            audio_files = []
            debug_msgs = []
            st.info(f"Current working directory: {os.getcwd()}")
            for scene_idx, scene in enumerate(parsed_script["scenes"]):
                narration_text = scene["text"]
                if not narration_text.strip():
                    continue
                output_path = f"voiceover_scene_{scene_idx}.mp3"
                st.write(f"[DEBUG] Scene {scene_idx}: narration_text='{narration_text[:60]}...' output_path='{output_path}'")
                try:
                    st.write(f"[DEBUG] Calling generate_voiceover_fallback for scene {scene_idx}")
                    generate_voiceover_fallback(narration_text, output_path)
                    st.write(f"[DEBUG] Returned from generate_voiceover_fallback for scene {scene_idx}")
                    # Debug: check if file exists and its size
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        debug_msgs.append(f"✅ File created: {output_path} ({file_size} bytes)")
                        audio_files.append(output_path)
                    else:
                        debug_msgs.append(f"❌ File NOT created: {output_path}")
                except Exception as e:
                    st.error(f"❌ Error generating voiceover for scene {scene_idx}: {e}")
                    debug_msgs.append(f"❌ Exception for scene {scene_idx}: {e}")
            if audio_files:
                st.session_state[audio_files_key] = audio_files
                st.session_state[gen_key] = True
                st.session_state[approve_key] = False
                st.session_state["auri_context"]["voiceover_files"] = audio_files
                st.session_state["executed_steps"][step_key] = f"{len(audio_files)} voiceover files generated."
                st.session_state["auri_context"]["step_outputs"][step_key] = st.session_state["executed_steps"][step_key]
            # Show debug info
            if debug_msgs:
                st.info("\n".join(debug_msgs))

        # Regenerate button
        if st.button("🔄 Regenerate Voiceovers"):
            do_generate()

        # Only show generate button if never generated
        if not st.session_state.get(gen_key):
            if st.button("🎙️ Generate Voiceovers"):
                do_generate()

        # Show audio and approve button if generated
        if st.session_state.get(gen_key):
            import base64
            audio_files = st.session_state.get(audio_files_key, [])
            st.markdown("### 🎧 Preview Voiceovers")
            for i, audio_path in enumerate(audio_files):
                st.markdown(f"**Scene {i+1}:**")
                # Check if file exists before trying to play or download
                if not os.path.exists(audio_path):
                    st.warning(f"Audio file not found: {audio_path}")
                    continue
                st.audio(audio_path)
                # Add download button
                try:
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="{audio_path}">⬇️ Download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Could not load audio for download: {e}")
            if not st.session_state.get(approve_key):
                if st.button("✅ Approve Voiceovers"):
                    st.session_state[approve_key] = True
                    st.success("Voiceovers approved!")
            else:
                st.success("Voiceovers approved!")
        return

    def handle_caption_hashtag_step():
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
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    def handle_thumbnail_step():
        from modules.thumbnail import generate_thumbnail
        result = generate_thumbnail(input_val or full_prompt)
        st.image(result, caption="Generated Thumbnail")
        st.session_state["executed_steps"][step_key] = "Thumbnail generated."
        st.session_state["auri_context"]["step_outputs"][step_key] = "Thumbnail generated."
        return

    def handle_schedule_post_step():
        from modules.scheduler import schedule_post
        result = schedule_post(input_val or full_prompt)
        st.success(result)
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    def handle_upload_step():
        result = f"📤 File received: {uploaded_file.name}" if uploaded_file else "No file uploaded"
        st.success(result)
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    def handle_default_step():
        result = "✅ Step complete — no handler yet."
        st.info(result)
        st.session_state["executed_steps"][step_key] = result
        st.session_state["auri_context"]["step_outputs"][step_key] = result
        return

    # Dispatcher logic
    if idx == 1 and is_idea_or_repurpose_step(step["title"], step["auri"]):
        return handle_idea_step()
    elif "script" in title:
        return handle_script_step()
    elif "voiceover" in title:
        return handle_voiceover_step()
    elif "caption" in title or "hashtag" in title:
        return handle_caption_hashtag_step()
    elif "thumbnail" in title or "image" in title:
        return handle_thumbnail_step()
    elif "schedule" in title or "post" in title:
        return handle_schedule_post_step()
    elif "upload" in title:
        return handle_upload_step()
    else:
        return handle_default_step()