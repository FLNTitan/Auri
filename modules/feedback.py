import streamlit as st
from datetime import datetime

def log_feedback(step_name, response, comment, language="English", platform="Web"):
    feedback = {
        "step": step_name,
        "response": response,
        "comment": comment,
        "timestamp": datetime.now().isoformat(),
        "language": language,
        "platform": platform,
    }
    print("FEEDBACK LOGGED:", feedback)
    if "auri_feedback" not in st.session_state:
        st.session_state["auri_feedback"] = []
    st.session_state["auri_feedback"].append(feedback)

def show_feedback_controls(step_key, step_title, regenerate_callback, language="English", platform="Web"):
    st.markdown("### 🔁 Regenerate or give feedback")

    with st.expander("🔁 Regenerate this step"):
        feedback_note = st.text_area(
            "Are there any specific changes you'd like me to make?",
            placeholder="Make it shorter and funnier (optional)",
            key=f"{step_key}_regen_note"
        )
        if st.button("🔄 Regenerate", key=f"{step_key}_regen_btn"):
            regenerate_callback(user_feedback=feedback_note)

    with st.expander("📝 Was this output helpful?"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Yes", key=f"{step_key}_yes"):
                log_feedback(step_title, "Yes", "", language, platform)
                st.success("Thanks!")
        with col2:
            if st.button("👎 No", key=f"{step_key}_no"):
                comment = st.text_area("What didn’t work?", key=f"{step_key}_no_comment")
                if st.button("Submit", key=f"{step_key}_submit_no"):
                    log_feedback(step_title, "No", comment, language, platform)
                    st.success("Thanks for your feedback!")
