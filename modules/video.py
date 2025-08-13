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
    # Allow both hyphen and en‑dash and optional spaces
    return bool(re.search(r'\d+s\s*[–-]\s*\d+s', script_text))

def determine_workflow(script_text: str) -> dict:
    needs_video = script_contains_time_ranges(script_text)
    needs_voiceover = needs_video
    needs_thumbnail = needs_video
    return {
        "needs_video": needs_video,
        "needs_voiceover": needs_voiceover,
        "needs_thumbnail": needs_thumbnail,
    }

def analyze_script(script_text: str) -> dict:
    """Parse a script breakdown into structured data.

    Each scene is defined by a time range (e.g. "0s–3s" or "4s-10s").
    Lines beginning with specific emojis map to scene attributes:
    🎥 camera direction, 💡 lighting notes, 🎶 music description, 🔄 transitions,
    🖼 on-screen text. Narration/voiceover lines begin with a ✅. They may
    contain quotes and/or a description before the quoted text. This function
    accumulates narration text for each scene, handling multiple narration
    lines per scene and extracting content from quotes or after a colon.
    """
    lines = script_text.splitlines()
    result = {
        "title": "",
        "goal": "",
        "delivery_notes": "",
        "equipment": "",
        "duration": "",
        "scenes": [],
    }
    current_scene: dict | None = None
    # Regex to match time ranges, allowing hyphens or en-dashes and optional spaces
    time_range_re = re.compile(r'(\d+)s\s*[–-]\s*(\d+)s')
    # Regex to capture quoted narration anywhere on a ✅ line
    narration_re = re.compile(r'^\s*✅.*?["“](.*?)["”]?$')
    camera_re = re.compile(r'^🎥\s*(.*)', re.IGNORECASE)
    lighting_re = re.compile(r'^💡\s*(.*)', re.IGNORECASE)
    music_re = re.compile(r'^🎶\s*(.*)', re.IGNORECASE)
    transition_re = re.compile(r'^🔄\s*(.*)', re.IGNORECASE)
    onscreen_re = re.compile(r'^🖼\s*(.*)', re.IGNORECASE)

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
                "onscreen_text": "",
            }
            # Extract any narration text that appears on the same line after the time range
            remaining = line[match.end():].strip()
            if remaining:
                # Remove leading symbols and quotes
                cleaned = remaining.lstrip('✅').strip(' –—:-').strip(' "“”')
                if cleaned:
                    current_scene["text"] = cleaned
            continue
        # Scene attributes
        if current_scene:
            # Check for camera, lighting, music, transition, onscreen markers
            cam = camera_re.match(line)
            if cam:
                current_scene["camera"] = cam.group(1).strip('" ')
                continue
            lig = lighting_re.match(line)
            if lig:
                current_scene["lighting"] = lig.group(1).strip('" ')
                continue
            mus = music_re.match(line)
            if mus:
                current_scene["music"] = mus.group(1).strip('" ')
                continue
            tra = transition_re.match(line)
            if tra:
                current_scene["transition"] = tra.group(1).strip('" ')
                continue
            ons = onscreen_re.match(line)
            if ons:
                current_scene["onscreen_text"] = ons.group(1).strip('" ')
                continue
            # Narration lines begin with a check mark
            if line.lstrip().startswith('✅'):
                # Try to extract quoted narration
                narr_match = narration_re.match(line)
                narration_text = narr_match.group(1).strip() if narr_match else ""
                if narration_text:
                    # Append or set narration text
                    if current_scene["text"]:
                        current_scene["text"] += " " + narration_text
                    else:
                        current_scene["text"] = narration_text
                    continue
                # Fallback: take text after a colon if no quotes present
                without_check = line.lstrip('✅').strip()
                if ':' in without_check:
                    after_colon = without_check.split(':', 1)[1].strip()
                    after_colon = after_colon.strip(' "“”')
                    if after_colon:
                        if current_scene["text"]:
                            current_scene["text"] += " " + after_colon
                        else:
                            current_scene["text"] = after_colon
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
        # Simple heuristic: require upload when visuals mention the user
        if any(keyword in visual.lower() for keyword in ["your", "personal", "custom"]):
            requires_user_upload = True
        planned.append({
            "scene_index": idx,
            "visual": visual,
            "onscreen_text": scene.get("onscreen_text", ""),
            "music": scene.get("music", ""),
            "transition": scene.get("transition", ""),
            "requires_user_upload": requires_user_upload,
            "suggested_source": "stock" if not requires_user_upload else "user_upload",
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
            "transition": scene["transition"],
        }
        assembly_plan.append(plan_item)
    return assembly_plan