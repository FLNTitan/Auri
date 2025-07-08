def handle_step_execution(idx, step, input_val, uploaded_file, full_prompt):
    step_key = f"step_{idx}"
    title = step["title"].lower()

    if idx == 1 and is_idea_or_repurpose_step(step["title"], step["auri"]):
        ideas = generate_ideas(full_prompt, input_val)
        result = "\n".join(ideas)
        for i, idea in enumerate(ideas, 1):
            clean_idea = re.sub(r"\[.*?\]", "", idea).strip()
            st.markdown(f"💡 **Idea {i}:** {clean_idea}")
        return

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
        workflow = determine_workflow(result)
        st.write("DEBUG workflow:", workflow)
        parsed_script = analyze_script(result)
        st.write("DEBUG parsed_script:", parsed_script)
        
        if workflow["needs_video"]:
            # Dynamically append video-related steps
            video_steps = [
                {
                    "title": "Plan Footage",
                    "auri": "I will analyze your script scenes and help you decide whether to upload footage or auto-generate visuals.",
                    "user": "Upload any video clips you'd like to use, or skip to auto-generate."
                },
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
        
            # Insert video steps immediately after the script step
            insertion_index = idx  # right after current step
            st.session_state["auri_steps"] = (
                st.session_state["auri_steps"][:insertion_index]
                + video_steps
                + st.session_state["auri_steps"][insertion_index:]
            )
            st.session_state["auri_context"]["video_workflow"] = workflow
            st.experimental_rerun()
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

        st.session_state["auri_context"]["captions"] = captions
        st.session_state["auri_context"]["hashtags"] = hashtags
        result = "\n\n---\n\n".join(combined_results)
        return

    elif "thumbnail" in title or "image" in title:
        from modules.thumbnail import generate_thumbnail
        result = generate_thumbnail(input_val or full_prompt)
        st.image(result, caption="Generated Thumbnail")
        return

    elif "schedule" in title or "post" in title:
        from modules.scheduler import schedule_post
        result = schedule_post(input_val or full_prompt)
        st.success(result)
        return

    elif "upload" in title:
        result = f"📤 File received: {uploaded_file.name}" if uploaded_file else "No file uploaded"
        st.success(result)
        return

    else:
        result = "✅ Step complete — no handler yet."
        st.info(result)
        return

    st.session_state["executed_steps"][step_key] = result
    st.session_state["auri_context"]["step_outputs"][step_key] = result

    return
