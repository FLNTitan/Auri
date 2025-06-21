from openai import OpenAI

def generate_caption(goal, platform, tone, idea, script, openai_key):
    if not all([goal, platform, tone, idea, script]):
        return "⚠️ Missing information to generate a caption."

    prompt = f"""
    You are Auri, an expert social media strategist.

    Here is the goal of the post: "{goal}"
    Here is the platform: {platform}
    Here is the tone: {tone}
    Here is the idea: "{idea}"
    Here is the full video script: 
    \"\"\"
    {script}
    \"\"\"

    Your job is to write a perfect caption for this post, optimized for {platform}.

    The caption should include:
    - A catchy hook (1st line)
    - Emojis (if platform appropriate)
    - Hashtags (relevant, not generic, 2–5 max)
    - A natural call-to-action (like “Follow for more”)
    - Line breaks and formatting that match {platform}'s style

    ⚠️ Do NOT repeat lines from the script or idea word-for-word.
    ✅ Make it feel human, native, and engaging.

    Output the final caption as a markdown block.
    """

    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating caption: {str(e)}"
