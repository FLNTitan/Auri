def content_idea_prompt(niche: str) -> str:
    return f"""
You are a social media strategist helping a content creator in the {niche} niche.
Suggest 5 fresh and specific content ideas that are short-form friendly (TikTok, Reels, Shorts).
Make sure the ideas:
- Hook attention fast
- Are relatable or trending
- Require low production effort

Output in a numbered list.
"""
