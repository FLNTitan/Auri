from openai import OpenAI

def generate_hashtags(goal, idea, script, platform, openai_key):
    if not all([goal, idea, script, platform]):
        return "⚠️ Missing information to generate hashtags."

    prompt = f"""
    You are Auri, an expert social media strategist.

    Your task is to generate 5–10 highly relevant, non-generic hashtags for the following content.

    • Goal: "{goal}"
    • Platform: {platform}
    • Idea: "{idea}"
    • Script: 
    \"\"\"
    {script}
    \"\"\"

    Guidelines:
    - Avoid overly generic tags like #foryou, #viral, #fun.
    - Include niche-specific, clever, or high-conversion tags.
    - Mix broad reach tags (1M+ posts) with niche-specific ones.
    - Tailor the hashtag strategy to the selected platform ({platform}).
    - Format the final hashtags in a clean **comma-separated list**, no explanations.

    Output ONLY the hashtags list.
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
        return f"⚠️ Error generating hashtags: {str(e)}"
