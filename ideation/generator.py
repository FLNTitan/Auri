from openai import OpenAI
from ideation.prompts import content_idea_prompt
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def is_idea_or_repurpose_step(title: str, auri_text: str) -> bool:
    keywords = [
        "idea", "repurpose", "reuse", "rework", "transform", "extract",
        "adapt", "use", "based on", "turn", "convert", "leverage", "past content", "existing"
    ]
    combined_text = f"{title} {auri_text}".lower()
    return any(kw in combined_text for kw in keywords)

def generate_ideas(full_prompt: str, user_input: str = None, count: int = 3):
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    system_prompt = f"""
You are Auri, an AI content strategist helping a creator generate viral content ideas.

The creator's goal is:
\"\"\"{full_prompt}\"\"\"

Additional input provided for this step (optional):
\"\"\"{user_input or "None"}\"\"\"

Your task:
- Generate exactly {count} unique content **ideas** (not scripts or plans)
- Each idea must align with the creator's overall goal (platform, format, audience)
- Incorporate the user's input if it helps improve relevance
- DO NOT include thumbnails, scripts, or scheduling details

Respond only in this format:
[Idea one]
[Idea two]
[Idea three]
.
.
.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip().split("\n")
