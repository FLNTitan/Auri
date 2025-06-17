def content_idea_prompt(goal: str) -> str:
    return f"""
You are a social media strategist AI assistant. A creator gave you this request: "{goal}"

Break it down into 3–6 clear steps in a content workflow. These steps may include:
- Generating ideas
- Writing scripts
- Creating thumbnails
- Editing video
- Scheduling posts

Output in a numbered list of actions, with each step short and clear.
"""
