import streamlit as st
from ideation.generator import generate_ideas

st.set_page_config(page_title="Auri | Dashboard", layout="centered")

st.markdown("### 👋 Hey Creator, what do we want to achieve today?")

col1, col2 = st.columns(2)
use_button = col1.button("🎯 Give me new content ideas")
custom_input = col2.text_input("Or tell me in your own words:")

if use_button:
    user_prompt = "Give me new content ideas"
elif custom_input:
    user_prompt = custom_input
else:
    user_prompt = None

if user_prompt:
    with st.spinner("Thinking..."):
        # For MVP we just treat all input as niche for now
        ideas = generate_ideas(user_prompt)
        st.success("Here are some ideas for you:")
        for idea in ideas:
            st.markdown(f"- {idea}")
