from openai import OpenAI
import streamlit as st
import re

def generate_script(goal, user_input=None, previous_output=None, user_instruction=None, platform="TikTok", tone="Informative"):

    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    prompt = f"""
    You are Auri, an expert short-form content director and social media scriptwriter.

    🧠 The user's overall goal:
    "{goal}"

    📋 What Auri asked from the user in this step:
    "{user_instruction or 'N/A'}"

    📥 User input for this step (specific idea or context):
    "{user_input or 'N/A'}"

    💡 Content ideas (from previous step):
    "{previous_output or 'N/A'}"

    🎯 For each content idea above, write a fully detailed video script suitable for {platform}.

    This script should be clear and actionable for small business owners, social media managers, or creators with limited production experience.

    Each script must include the following sections:

    1. **🎬 Title** – Catchy, short title for the piece.
    2. **🎯 Goal** – Purpose of the video: Educate, Inspire, Entertain, or Sell.
    3. **🧲 Hook** – First 1–3 seconds to grab attention.
    4. **📜 Full Script Breakdown** – Step-by-step narration or action plan.
    - Use **timestamps** (e.g. “0s–3s”, “3s–6s”, etc.)
    - For each timestamp, include:
        - ✅ What to say/do
        - 🎥 Camera direction (shot type: close-up, selfie, overhead, etc.)
        - 💡 Lighting suggestion (e.g. natural light, ring light, etc.)
        - 🎶 Music style suggestion (or trending sound type)
        - 🔄 Transition (e.g. snap cut, zoom, match cut) if needed
        - 🖼 On-screen text (if any)
        - 🎬 Optional B-roll or cutaway notes

    5. **🎤 Delivery Notes** – Tone of voice or energy (e.g. calm, confident, excited).

    6. **🛠 Recommended Equipment (if any)** – Keep it simple and affordable: smartphone, tripod, mic, etc.

    7. **⏱ Total Estimated Duration** – Approximate total video length (e.g. 15s, 30s).

    ⚠️ DO NOT include anything about:
    - Thumbnails or captions
    - Scheduling or posting
    - Hashtags or analytics
    - Anything Auri will handle in other steps

    - At least ONE script must clearly incorporate the user input (if there is any input given).

    🧾 Format strictly as markdown with headers for each section. Separate ideas with clear dividers.

    Be concise and platform native.
    """


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def generate_script_step_instruction(client, idea_text, platform="Instagram", tone="Informative"):
    micro_prompt = f"""
        You are Auri. The user gave you this idea to develop into a video script:
        "{idea_text}"

        Generate a single step for "Script Writing" in the same format as other steps, including:
        1. A short and clear step title.
        2. "I will..." – What Auri will do to write the script.
        3. "To do that, I’ll need you to..." – A specific and polite request to the user, e.g. platform/tone input.

        Use this strict format:
        Script Writing | I will... | To do that, I’ll need you to...

        Only generate that one line. Keep it clean and clear.
        """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": micro_prompt}],
        temperature=0.3,
    )
    line = response.choices[0].message.content.strip()
    match = re.match(r"^\s*Script Writing\s+\|\s+(I will.*?)\s+\|\s+(To do that.*?)$", line)
    if match:
        return {
            "title": "Script Writing",
            "auri": match.group(1).strip(),
            "user": match.group(2).strip()
        }
    return None
