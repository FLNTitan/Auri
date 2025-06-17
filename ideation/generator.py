from openai import OpenAI
from ideation.prompts import content_idea_prompt
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def generate_ideas(user_goal: str) -> list:
    prompt = content_idea_prompt(user_goal)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
    )

    content = response.choices[0].message.content
    return [line.strip("•-123. ").strip() for line in content.strip().split("\n") if line.strip()]
