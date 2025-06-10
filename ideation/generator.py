import openai
from ideation.prompts import content_idea_prompt

def generate_ideas(niche: str) -> list:
    prompt = content_idea_prompt(niche)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    content = response["choices"][0]["message"]["content"]
    return content.split("\n")
