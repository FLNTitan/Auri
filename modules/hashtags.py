from openai import OpenAI

def generate_hashtags(goal, idea, script, platform, openai_key):
    if not all([goal, idea, script, platform]):
        return "⚠️ Missing information to generate hashtags."

    prompt = f"""
You are Auri, an expert social media strategist.

Your task is to generate a list of 5–10 highly relevant, non-generic hashtags for the given video content.

🧠 Context:
- Goal: "{goal}"
- Platform: {platform}
- Idea: "{idea}"
- Script:
\"\"\"
{script}
\"\"\"

📝 Guidelines:
- No generic tags like #foryou, #viral, #fun
- Include niche-relevant, clever, or trending tags
- Mix high-reach (1M+) with niche-specific ones
- Customize for {platform} audience behavior
- Return hashtags as a **comma-separated list** only — no titles, no explanation.

Output format:
#tag1, #tag2, #tag3, ...
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
        return f"⚠️ Error generating hashtags: {e}"
