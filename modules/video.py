import re


def clean_label(text, prefix):
    """Remove a prefix label and extra quotes/spaces."""
    return re.sub(
        rf"^{re.escape(prefix)}\s*",
        "",
        text,
        flags=re.I
    ).strip().strip('"')

def detect_video_ideas(ideas: list[str]) -> bool:
    video_keywords = ["reel", "short", "tiktok", "voiceover", "video", "skit", "b-roll"]
    return any(any(kw in idea.lower() for kw in video_keywords) for idea in ideas)

def script_contains_time_ranges(script_text: str) -> bool:
    return bool(re.search(r'\d+s\s*–\s*\d+s', script_text))

def determine_workflow(script_text: str) -> dict:
    needs_video = script_contains_time_ranges(script_text)
    needs_voiceover = needs_video
    needs_thumbnail = needs_video

    return {
        "needs_video": needs_video,
        "needs_voiceover": needs_voiceover,
        "needs_thumbnail": needs_thumbnail
    }


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

    # Compile regexes
    time_range_re = re.compile(r'(\d+)s[–-](\d+)s')
    camera_re = re.compile(r'🎥\s*(.*)', re.IGNORECASE)
    lighting_re = re.compile(r'💡\s*(.*)', re.IGNORECASE)
    music_re = re.compile(r'🎶\s*(.*)', re.IGNORECASE)
    transition_re = re.compile(r'🔄\s*(.*)', re.IGNORECASE)
    onscreen_re = re.compile(r'🖼\s*(.*)', re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for scene start
        match = time_range_re.search(line)
        if match:
            # Save previous scene
            if current_scene:
                result["scenes"].append(current_scene)
            
            start_seconds = int(match.group(1))
            end_seconds = int(match.group(2))

            current_scene = {
                "start": f"{start_seconds}s",
                "end": f"{end_seconds}s",
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "text": "",
                "camera": "",
                "lighting": "",
                "music": "",
                "transition": "",
                "onscreen_text": ""
            }
            # Try to extract text after time range
            parts = line.split(match.group(0))
            if len(parts) > 1:
                current_scene["text"] = parts[1].strip("–—: ").strip("✅").strip('" ')
            continue
        
        # Scene attributes
        if current_scene:
            cam = camera_re.search(line)
            if cam:
                current_scene["camera"] = cam.group(1).strip('" ')
                continue
            lig = lighting_re.search(line)
            if lig:
                current_scene["lighting"] = lig.group(1).strip('" ')
                continue
            mus = music_re.search(line)
            if mus:
                current_scene["music"] = mus.group(1).strip('" ')
                continue
            tra = transition_re.search(line)
            if tra:
                current_scene["transition"] = tra.group(1).strip('" ')
                continue
            ons = onscreen_re.search(line)
            if ons:
                current_scene["onscreen_text"] = ons.group(1).strip('" ')
                continue

    # Append last scene
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
            "onscreen_text": scene.get("onscreen_text", ""),
            "music": scene.get("music", ""),
            "transition": scene.get("transition", ""),
            "requires_user_upload": requires_user_upload,
            "suggested_source": "stock" if not requires_user_upload else "user_upload"
        })
    return planned


def build_assembly_plan(planned_footage, scene_selections):
    assembly_plan = []
    for scene in planned_footage:
        scene_key = f"scene_{scene['scene_index']}"
        selection = scene_selections.get(scene_key, {})
        plan_item = {
            "scene_index": scene["scene_index"],
            "use_stock": selection.get("use_stock", False),
            "filename": selection.get("filename"),
            "visual": scene["visual"],
            "onscreen_text": scene["onscreen_text"],
            "music": scene["music"],
            "transition": scene["transition"]
        }
        assembly_plan.append(plan_item)
    return assembly_plan
