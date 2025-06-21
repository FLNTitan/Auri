from openai import OpenAI

def generate_caption(goal, platform, tone, idea, script, openai_key, language="English"):
    if not all([goal, platform, tone, idea, script]):
        return "⚠️ Missing information to generate a caption."

    if language == "עברית":
        prompt = f"""
אתה Auri, מומחה לאסטרטגיית תוכן ברשתות חברתיות.

🎯 מטרת הפוסט: "{goal}"
📱 פלטפורמה: {platform}
🎭 טון: {tone}
💡 רעיון: "{idea}"
📜 תסריט וידאו:
\"\"\"
{script}
\"\"\"

המטרה שלך היא לכתוב כיתוב מושלם לפוסט הזה, מותאם לפלטפורמה {platform}.

יש לכלול:
- שורת פתיחה מושכת (hook)
- אימוג'ים (רק אם מתאימים לפלטפורמה)
- קריאה לפעולה טבעית (למשל “עקבו לעוד”)
- עיצוב שורות שמתאים לפלטפורמה {platform}

⚠️ אל תחזור מילה במילה על התסריט או הרעיון.
✅ תכתוב כמו בן אדם — בצורה אותנטית, מושכת, וקלה לקריאה.

📦 החזר את הכיתוב כבלוק Markdown בלבד.
"""
    else:
        prompt = f"""
You are Auri, an expert social media strategist.

🎯 Goal: "{goal}"
📱 Platform: {platform}
🎭 Tone: {tone}
💡 Idea: "{idea}"
📜 Script:
\"\"\"
{script}
\"\"\"

Your job is to write a perfect caption for this post, optimized for {platform}.

Include:
- A catchy hook (1st line)
- Emojis (if platform appropriate)
- A natural call-to-action (like “Follow for more”)
- Line breaks and formatting that match {platform}'s style
- ⚠️ DO NOT include hashtags (they are handled separately)
- ⚠️ DO NOT repeat script or idea lines verbatim
- ✅ Make it feel human, natural, and engaging

📦 Output the caption as a **markdown block only**, no explanations.
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
