from openai import OpenAI
from ideation.prompts import content_idea_prompt
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def generate_ideas(user_goal: str) -> list:
    prompt = content_idea_prompt(user_goal)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're an expert content strategist. Break down user goals into actionable content steps."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content

    # Clean and split into workflow steps
    lines = content.split("\n")
    steps = [line.strip("•-123. ").strip() for line in lines if line.strip()]
    return steps