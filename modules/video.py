import re

def detect_video_ideas(ideas: list[str]) -> bool:
    video_keywords = ["reel", "short", "tiktok", "voiceover", "video", "skit", "b-roll"]
    return any(any(kw in idea.lower() for kw in video_keywords) for idea in ideas)

def analyze_script(script_text: str) -> dict:
    lines = script_text.splitlines()
    
    result = {
        "title": "",
        "goal": "",
        "delivery_notes": "",
        "equipment": "",
        "duration": "",
        "scenes": []
    }
    
    current_scene = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Header
        if line.startswith("🎬 Title:"):
            result["title"] = line.split("🎬 Title:")[1].strip()
        elif line.startswith("🎯 Goal:"):
            result["goal"] = line.split("🎯 Goal:")[1].strip()
        elif line.startswith("🎤 Delivery Notes"):
            result["delivery_notes"] = line.replace("🎤 Delivery Notes","").strip()
        elif line.startswith("🛠 Recommended Equipment"):
            result["equipment"] = line.replace("🛠 Recommended Equipment","").strip()
        elif line.startswith("⏱ Total Estimated Duration"):
            result["duration"] = line.replace("⏱ Total Estimated Duration","").strip()
        
        # Scene start
        scene_match = re.match(r'^(\d+s–\d+s):\s*"(.*?)"', line)
        if scene_match:
            if current_scene:
                result["scenes"].append(current_scene)
            start_end = scene_match.group(1)
            text = scene_match.group(2)
            start, end = start_end.split("–")
            current_scene = {
                "start": start.strip(),
                "end": end.strip(),
                "text": text,
                "camera": "",
                "lighting": "",
                "music": "",
                "transition": "",
                "onscreen_text": ""
            }
            continue
        
        # Attributes
        if current_scene:
            if line.startswith("🎥 Camera direction:"):
                current_scene["camera"] = line.split("🎥 Camera direction:")[1].strip()
            elif line.startswith("💡 Lighting suggestion:"):
                current_scene["lighting"] = line.split("💡 Lighting suggestion:")[1].strip()
            elif line.startswith("🎶 Music style suggestion:"):
                current_scene["music"] = line.split("🎶 Music style suggestion:")[1].strip()
            elif line.startswith("🔄 Transition:"):
                current_scene["transition"] = line.split("🔄 Transition:")[1].strip()
            elif line.startswith("🖼 On-screen text:"):
                current_scene["onscreen_text"] = line.split("🖼 On-screen text:")[1].strip()
    
    # Append the last scene
    if current_scene:
        result["scenes"].append(current_scene)
    
    return result


def plan_footage(scenes: list) -> list:
    planned = []
    for idx, scene in enumerate(scenes):
        visual = scene.get("camera", "")
        requires_user_upload = False
        
        # Simple heuristic (you can improve this)
        if any(keyword in visual.lower() for keyword in ["your", "personal", "custom"]):
            requires_user_upload = True
        
        planned.append({
            "scene_index": idx,
            "visual": visual,
            "requires_user_upload": requires_user_upload,
            "suggested_source": "stock" if not requires_user_upload else "user_upload"
        })
    return planned
