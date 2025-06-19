from openai import OpenAI
import streamlit as st

def generate_script(goal, user_input=None, previous_output=None, platform="TikTok", tone="Informative"):
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    prompt = f"""
You are Auri, an AI scriptwriting assistant for social media.

🧠 User’s original goal:
"{goal}"

📝 User input for this step:
"{user_input or "N/A"}"

📦 Output of previous step:
"{previous_output or "N/A"}"

🎯 Your task:
Write a {tone.lower()} script for {platform}.

Structure:
- Hook
- 2–3 Key Points
- Call-to-Action (CTA)

Be concise, platform-native, and engaging.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()