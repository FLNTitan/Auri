# modules/script.py
from openai import OpenAI
import streamlit as st

def generate_script(prompt, platform="TikTok", tone="Informative"):
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    system_prompt = f"""
    You are a scriptwriting assistant for social media.
    The platform is: {platform}
    The desired tone is: {tone}

    Based on the following idea or goal, generate a compelling short-form content script:
    \"{prompt}\"

    Structure it as:
    - Hook
    - 2–3 Key Points
    - Call-to-Action (CTA)

    Be concise, engaging, and on-brand for the platform.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
