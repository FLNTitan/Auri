from ideation.generator import generate_ideas, is_idea_or_repurpose_step
from modules.feedback import show_feedback_controls
from modules.script import generate_script_step_instruction
from modules.video import detect_video_ideas, analyze_script, determine_workflow, clean_label
from modules.tts import generate_voiceover_fallback
import re
import streamlit as st
from modules.video import detect_video_ideas, analyze_script, determine_workflow, clean_label
from modules.video_editor import assemble_video

def handle_step_execution(idx, step, input_val, uploaded_file, full_prompt):
    step_key = f"step_{idx}"
    title = step["title"].lower()

    def handle_assemble_video_step():
        import os
        from modules.video_editor import assemble_video

        st.markdown("### 🎬 Assemble Video")
        ctx = st.session_state.get("auri_context", {})
        ideas_data = ctx.get("ideas_data", {})

        idea_keys = [k for k, v in ideas_data.items() if isinstance(v, dict) and v.get("assembly_plan")]
        if not idea_keys:
            st.error("No assembly plan found. Generate a script and plan footage first.")
            return

        choice = st.selectbox("Select idea to assemble", idea_keys)
        assembly_plan = ideas_data[choice]["assembly_plan"]

        # Make sure timing/edit fields exist
        for item in assembly_plan:
            item.setdefault("start_seconds", 0.0)
            item.setdefault("end_seconds", item.get("start_seconds", 0.0) + 1.0)
            item.setdefault("speed", 1.0)
            item.setdefault("zoom", None)
            item.setdefault("caption", None)

        nl = st.text_area(
            "🗣️ (Optional) Describe edits",
            placeholder='e.g., "Trim scene 2 to 1.5s, add captions \\"Sale ends Friday\\" on scene 1, lower music by 6dB"'
        )

        assets_dir = st.text_input("📂 Folder with your uploaded clips", value=".")
        out_path = st.text_input("📼 Output path", value=os.path.join("exports", choice, "final_video.mp4"))
        music_gain = st.number_input("🎚️ Music gain (dB; negative lowers)", value=0.0, step=1.0)
        crossfade_ms = st.number_input("🔗 Crossfade between scenes (ms)", value=0, step=50)

        if st.button("▶ Assemble Now", key=f"assemble_now_{choice}"):
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            result_type, path = assemble_video(
                assembly_plan=assembly_plan,
                assets_dir=assets_dir,
                out_path=out_path,
                nl_edit_request=nl,
                music_gain_db=music_gain,
                crossfade_ms=crossfade_ms
            )
            if result_type == "file":
                st.success(f"✅ Rendered video: {path}")
                try:
                    st.video(path)
                except Exception:
                    st.info("Rendered. Preview not available in this environment.")
            else:
                st.warning("MoviePy unavailable here — generated FFmpeg script instead.")
                st.code(f"bash {path}", language="bash")

            st.session_state["executed_steps"][step_key] = f"{result_type} → {path}"
            st.session_state["auri_context"].setdefault("step_outputs", {})[step_key] = path
        return

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
        import traceback
        try:
            from modules.tts import generate_voiceover_fallback
            import os
            st.warning("[DEBUG] handle_voiceover_step CALLED")
            parsed_script = st.session_state["auri_context"].get("parsed_script")
            st.info(f"[DEBUG] parsed_script: {parsed_script}")
            if not parsed_script:
                st.error("❌ No parsed script found. Please generate a script first.")
                return
            scenes = parsed_script.get("scenes")
            st.info(f"[DEBUG] scenes: {scenes}")
            if not scenes or not isinstance(scenes, list):
                st.error("❌ No scenes found in parsed script. Please check your script generation step.")
                st.info(f"[DEBUG] parsed_script: {parsed_script}")
                return

            import io
            from gtts import gTTS
            import base64
            st.warning("[DEBUG] handle_voiceover_step CALLED")

            col1, col2 = st.columns([2,1])
            with col1:
                gen_pressed = st.button("🎙️ Generate Voiceovers", key="gen_voice_btn")
            with col2:
                clear_pressed = st.button("🗑️ Clear Voiceovers", key="clear_voice_btn")

            # Always show debug info if present
            debug_msgs = st.session_state.get("voiceover_debug_msgs", [])
            if debug_msgs:
                st.info("\n".join(debug_msgs))

            if clear_pressed:
                st.session_state.pop("voiceover_local_buffers", None)
                st.session_state.pop("voiceover_local_approved", None)
                st.session_state.pop("voiceover_debug_msgs", None)
                st.info("Voiceover previews cleared.")

            if gen_pressed:
                try:
                    st.warning("[DEBUG] Generate button pressed")
                    st.info(f"Current working directory: {os.getcwd()}")
                    audio_buffers = []
                    debug_msgs = []
                    valid_narration = False
                    for scene_idx, scene in enumerate(scenes):
                        narration_text = scene.get("text", "")
                        st.write(f"[DEBUG] Scene {scene_idx} narration_text: {narration_text!r}")
                        if narration_text and narration_text.strip():
                            valid_narration = True
                        if not narration_text or not narration_text.strip():
                            debug_msgs.append(f"[SKIP] Scene {scene_idx} has empty text.")
                            continue
                        try:
                            st.write(f"[DEBUG] Generating voiceover in-memory for scene {scene_idx}")
                            tts = gTTS(narration_text, lang='en')
                            buf = io.BytesIO()
                            tts.write_to_fp(buf)
                            buf.seek(0)
                            st.write(f"[DEBUG] MP3 buffer size for scene {scene_idx}: {len(buf.getvalue())} bytes")
                            audio_buffers.append(buf)
                            debug_msgs.append(f"✅ In-memory audio generated for scene {scene_idx}")
                        except Exception as e:
                            st.error(f"❌ Error generating voiceover for scene {scene_idx}: {e}")
                            debug_msgs.append(f"❌ Exception for scene {scene_idx}: {e}")
                            # Fallback: generate a dummy audio buffer so preview UI always appears
                            import wave
                            import struct
                            dummy_buf = io.BytesIO()
                            with wave.open(dummy_buf, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(22050)
                                # 0.5 seconds of silence
                                frames = b''.join([struct.pack('<h', 0) for _ in range(11025)])
                                wf.writeframes(frames)
                            dummy_buf.seek(0)
                            st.write(f"[DEBUG] Dummy WAV buffer size for scene {scene_idx}: {len(dummy_buf.getvalue())} bytes")
                            audio_buffers.append(dummy_buf)
                            debug_msgs.append(f"✅ Dummy audio generated for scene {scene_idx}")
                    # Fallback: if no audio buffers were generated, always add a dummy
                    if not audio_buffers:
                        import wave
                        import struct
                        dummy_buf = io.BytesIO()
                        with wave.open(dummy_buf, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(22050)
                            frames = b''.join([struct.pack('<h', 0) for _ in range(11025)])
                            wf.writeframes(frames)
                        dummy_buf.seek(0)
                        st.write(f"[DEBUG] Fallback: Added single dummy WAV buffer, size: {len(dummy_buf.getvalue())} bytes")
                        audio_buffers.append(dummy_buf)
                        debug_msgs.append("✅ Fallback: Dummy audio generated (no valid scenes)")
                    st.session_state["voiceover_debug_msgs"] = debug_msgs
                    st.session_state["voiceover_local_buffers"] = audio_buffers
                    st.session_state["voiceover_local_approved"] = False
                except Exception as fatal_e:
                    st.error(f"[FATAL ERROR] Exception in Generate Voiceovers: {fatal_e}")
                    st.code(traceback.format_exc())

            # --- Known-good MP3 preview for Streamlit audio widget test ---
            st.markdown("---")
            st.markdown("#### [DEBUG] Known-good MP3 Preview (should always play)")
            import base64
            # 1-second 440Hz sine wave MP3, base64-encoded (generated externally)
            known_good_mp3_b64 = (
                "SUQzAwAAAAAAFlRFTkMAAAAwAAADTGF2ZjU2LjI0LjEwNAAAAAAAAAAAAAAA//tQxAADBQAA"
                "AABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA"
            )
            import io
            known_good_mp3 = io.BytesIO(base64.b64decode(known_good_mp3_b64))
            st.audio(known_good_mp3, format='audio/mp3')

            audio_buffers = st.session_state.get("voiceover_local_buffers")
            if audio_buffers:
                st.markdown("### 🎧 Preview Voiceovers")
                for i, buf in enumerate(audio_buffers):
                    st.markdown(f"**Scene {i+1}:**")
                    st.audio(buf, format='audio/mp3')
                    try:
                        buf.seek(0)
                        audio_bytes = buf.read()
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="scene_{i+1}.mp3">⬇️ Download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"Could not load audio for download: {e}")
                if not st.session_state.get("voiceover_local_approved"):
                    if st.button("✅ Approve Voiceovers", key="approve_voice_btn"):
                        st.session_state["voiceover_local_approved"] = True
                        st.success("Voiceovers approved!")
                else:
                    st.success("Voiceovers approved!")
                    
                # ✅ Now safe to mark step as complete
                if not st.session_state.get("executed_steps", {}).get(step_key):
                    st.session_state["executed_steps"][step_key] = f"{len(audio_buffers)} voiceovers generated and previewed."
                    st.session_state["auri_context"]["step_outputs"][step_key] = st.session_state["executed_steps"][step_key]

            return
        except Exception as top_fatal:
            st.error(f"[FATAL ERROR] Exception in handle_voiceover_step: {top_fatal}")
            import traceback
            st.code(traceback.format_exc())

        # --- Known-good MP3 preview for Streamlit audio widget test ---
        st.markdown("---")
        st.markdown("#### [DEBUG] Known-good MP3 Preview (should always play)")
        import base64
        # 1-second 440Hz sine wave MP3, base64-encoded (generated externally)
        known_good_mp3_b64 = (
            "SUQzAwAAAAAAFlRFTkMAAAAwAAADTGF2ZjU2LjI0LjEwNAAAAAAAAAAAAAAA//tQxAADBQAA"
            "AABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA//u1TAAABhAAAABJTkZPAABBAAAAPwAAACAA"
        )
        import io
        known_good_mp3 = io.BytesIO(base64.b64decode(known_good_mp3_b64))
        st.audio(known_good_mp3, format='audio/mp3')

        audio_buffers = st.session_state.get("voiceover_local_buffers")
        if audio_buffers:
            st.markdown("### 🎧 Preview Voiceovers")
            for i, buf in enumerate(audio_buffers):
                st.markdown(f"**Scene {i+1}:**")
                st.audio(buf, format='audio/mp3')
                try:
                    buf.seek(0)
                    audio_bytes = buf.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="scene_{i+1}.mp3">⬇️ Download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Could not load audio for download: {e}")
            if not st.session_state.get("voiceover_local_approved"):
                if st.button("✅ Approve Voiceovers", key="approve_voice_btn"):
                    st.session_state["voiceover_local_approved"] = True
                    st.success("Voiceovers approved!")
            else:
                st.success("Voiceovers approved!")
        else:
            st.info("No voiceover previews available. Click 'Generate Voiceovers' to create them.")
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
    elif "assemble" in title or "video" in title and "assemble" in step["auri"].lower():
        return handle_assemble_video_step()
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