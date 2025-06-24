import streamlit as st
from datetime import datetime
from supabase import create_client
import os

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_feedback(step_name, response, comment, language="English", platform="Web"):
    feedback = {
        "timestamp": datetime.now().isoformat(),
        "step": step_name,
        "response": response,
        "comment": comment,
        "language": language,
        "platform": platform,
        "user_id": st.session_state.get("user_id", "anon"),
        "workflow_goal": st.session_state.get("auri_context", {}).get("goal", ""),
        "regenerated": st.session_state.get(f"{step_name}_regenerated", False)
    }

    if "auri_feedback" not in st.session_state:
        st.session_state["auri_feedback"] = []
    st.session_state["auri_feedback"].append(feedback)

    supabase.table("feedback").insert(feedback).execute()

def show_feedback_controls(step_key, step_title, regenerate_callback, language="English", platform="Web"):
    feedback_state = f"{step_key}_feedback_state"

    if feedback_state not in st.session_state:
        st.session_state[feedback_state] = {"submitted": False, "response": None}

    st.markdown("#### 🔁 Regenerate or Give Feedback")

    # --- Regenerate Section ---
    with st.expander("🔁 Regenerate this step"):
        feedback_note = st.text_area(
            "Are there any specific changes you'd like me to make?",
            placeholder="Make it shorter and funnier (optional)",
            key=f"{step_key}_regen_note"
        )
        if st.button("🔄 Regenerate", key=f"{step_key}_regen_btn"):
            regenerate_callback(user_feedback=feedback_note)

    # --- Feedback Section ---
    submitted = st.session_state[feedback_state]["submitted"]
    response = st.session_state[feedback_state]["response"]

    if not submitted:
        st.markdown("##### 🤔 Did Auri answer your needs in this step?")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Yes", key=f"{step_key}_yes"):
                st.session_state[feedback_state] = {"submitted": True, "response": "Yes"}
                log_feedback(step_title, "Yes", "", language, platform)
                st.rerun()  # Immediately refresh to disable buttons

        with col2:
            if st.button("👎 No", key=f"{step_key}_no"):
                st.session_state[feedback_state]["response"] = "No"

        if response == "No":
            comment = st.text_area("💬 What went wrong?", key=f"{step_key}_no_comment")
            if st.button("Submit", key=f"{step_key}_submit_no"):
                st.session_state[feedback_state]["submitted"] = True
                log_feedback(step_title, "No", comment, language, platform)
                st.rerun()

    elif submitted:
        st.markdown("##### 🤔 Was this step helpful?")
        col1, col2 = st.columns(2)

        with col1:
            st.button("👍 Yes", key=f"{step_key}_yes_disabled", disabled=True)

        with col2:
            st.button("👎 No", key=f"{step_key}_no_disabled", disabled=True)

        st.success("✅ Thank you for your feedback!")
        st.success("✅ Step completed.")
        st.info("👉 Ready to move to the next step?")
