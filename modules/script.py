def generate_script(goal, user_input=None, previous_output=None, platform="TikTok", tone="Informative"):
    from openai import OpenAI
    import streamlit as st

    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    prompt = f"""
You are Auri, an AI scriptwriting assistant.

🧠 The user's goal:
\"{goal}\"

📥 Input the user gave for this step:
\"{user_input or "N/A"}\"

💡 Ideas from the previous step:
\"{previous_output or "N/A"}\"

🎯 Write a separate, short {platform} script for each idea above. 
Each script should include:
- A hook line
- 2–3 key points
- A closing line or CTA

Use a {tone.lower()} tone. Format each script clearly with its title.
Return only the scripts. No commentary.

Be concise, platform native and engaging
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
