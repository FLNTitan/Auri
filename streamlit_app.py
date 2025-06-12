import streamlit as st
from ideation.generator import generate_ideas

st.set_page_config(page_title="Auri – Your AI Copilot", layout="centered")

# Marker for styling
st.write('<span id="main_content_marker"></span>', unsafe_allow_html=True)

# Inject CSS
st.markdown("""
<style>
html, body, [class*="css"] {
  background-color: #F4F7FA !important;
  font-family: 'Segoe UI', sans-serif;
}
div[data-testid="stVerticalBlock"]:has(#main_content_marker) {
  margin-top: 3rem;
  padding: 2rem;
  background-color: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
h1 { color: #6C63FF; font-size: 2.6rem; }
h3 { color: #1F2937; }
input {
  background-color: #FFFFFF !important;
  color: #1F2937 !important;
  border-radius: 6px;
  padding: 0.5rem;
}
button {
  background-color: #6C63FF !important;
  color: white !important;
  border: none !important;
  padding: 0.5rem 1.5rem !important;
  border-radius: 0.5rem;
}
button:hover { background-color: #574FD6 !important; }
</style>
""", unsafe_allow_html=True)

# UI content
st.markdown("## 👋 Hey there, I’m Auri")
st.markdown("### What do you want to achieve today?")

col1, col2 = st.columns(2)
if col1.button("🎯 Give me new content ideas"):
    st.session_state['prompt'] = "Generate 5 content ideas"
custom = col2.text_input("Or type your own request")

if "prompt" in st.session_state or custom:
    prompt = st.session_state.get('prompt', custom)
    st.markdown(f"💡 **Auri's thinking about:** _{prompt}_")
    ideas = generate_ideas(prompt)
    for idea in ideas:
        if idea.strip():  # show bullet only if not empty
            st.markdown(f"- {idea}")
        else:
            st.markdown(" ")  # insert a spacer if needed
