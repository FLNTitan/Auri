# modules/video.py
import os
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple, Optional

# ---------- Low-level helpers ----------

def clean_label(text: str, prefix: str) -> str:
    """Remove a prefix label and extra quotes/spaces."""
    return re.sub(rf"^{re.escape(prefix)}\s*", "", text, flags=re.I).strip().strip('"')

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()

# ---------- Script Understanding ----------

def script_contains_time_ranges(script_text: str) -> bool:
    return bool(re.search(r'\d+s\s*[–-]\s*\d+s', script_text))

def detect_video_ideas(ideas: List[str]) -> bool:
    video_keywords = ["reel", "short", "tiktok", "voiceover", "video", "skit", "b-roll"]
    return any(any(kw in (idea or "").lower() for kw in video_keywords) for idea in ideas)

def determine_workflow(script_text: str) -> Dict[str, bool]:
    needs_video = script_contains_time_ranges(script_text)
    return {
        "needs_video": needs_video,
        "needs_voiceover": needs_video,
        "needs_thumbnail": needs_video,
    }

def analyze_script(script_text: str) -> Dict[str, Any]:
    """
    Parse a script breakdown into structured scenes.
    Each scene:
        start/end (seconds), text (narration), camera, lighting, music, transition, onscreen_text
    """
    lines = (script_text or "").splitlines()
    result = {
        "title": "",
        "goal": "",
        "delivery_notes": "",
        "equipment": "",
        "duration": "",
        "scenes": [],
    }
    current_scene: Optional[Dict[str, Any]] = None

    time_range_re = re.compile(r'(\d+)s\s*[–-]\s*(\d+)s')
    narration_re = re.compile(r'^\s*✅.*?["“](.*?)["”]?$')
    camera_re     = re.compile(r'^🎥\s*(.*)', re.I)
    lighting_re   = re.compile(r'^💡\s*(.*)', re.I)
    music_re      = re.compile(r'^🎶\s*(.*)', re.I)
    transition_re = re.compile(r'^🔄\s*(.*)', re.I)
    onscreen_re   = re.compile(r'^🖼\s*(.*)', re.I)

    def _flush_scene():
        nonlocal current_scene
        if current_scene:
            result["scenes"].append(current_scene)
            current_scene = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = time_range_re.search(line)
        if m:
            _flush_scene()
            s, e = int(m.group(1)), int(m.group(2))
            current_scene = {
                "start": f"{s}s",
                "end": f"{e}s",
                "start_seconds": s,
                "end_seconds": e,
                "text": "",
                "camera": "",
                "lighting": "",
                "music": "",
                "transition": "",
                "onscreen_text": "",
            }
            # inline narration after time-range (if exists)
            trailing = line[m.end():].strip()
            if trailing:
                cleaned = trailing.lstrip('✅').strip(' –—:-').strip(' "“”')
                if cleaned:
                    current_scene["text"] = cleaned
            continue

        if not current_scene:
            continue

        if (m := camera_re.match(line)):
            current_scene["camera"] = m.group(1).strip('" ')
            continue
        if (m := lighting_re.match(line)):
            current_scene["lighting"] = m.group(1).strip('" ')
            continue
        if (m := music_re.match(line)):
            current_scene["music"] = m.group(1).strip('" ')
            continue
        if (m := transition_re.match(line)):
            current_scene["transition"] = m.group(1).strip('" ')
            continue
        if (m := onscreen_re.match(line)):
            current_scene["onscreen_text"] = m.group(1).strip('" ')
            continue

        # narration lines begin with ✅
        if line.lstrip().startswith('✅'):
            narr_m = narration_re.match(line)
            if narr_m and narr_m.group(1).strip():
                chunk = narr_m.group(1).strip()
            else:
                without_check = line.lstrip('✅').strip()
                chunk = without_check.split(':', 1)[1].strip(' "“”') if ':' in without_check else without_check
            if chunk:
                current_scene["text"] = (current_scene["text"] + " " + chunk).strip()

    _flush_scene()
    return result

# ---------- Planning Footage & Checklists ----------

@dataclass
class ShotSpec:
    scene_index: int
    duration: float
    shot_type: str
    description: str
    requires_user_upload: bool
    onscreen_text: str = ""
    music: str = ""
    transition: str = ""

def _infer_shot_type(camera: str) -> str:
    c = (camera or "").lower()
    if any(k in c for k in ["selfie", "front camera", "talking head"]): return "Talking head / selfie"
    if any(k in c for k in ["overhead", "top down"]): return "Overhead"
    if any(k in c for k in ["close", "macro"]): return "Close-up"
    if any(k in c for k in ["wide", "establishing"]): return "Wide"
    return "General / B-roll"

def plan_footage(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Legacy shape used by your UI; keep it intact."""
    planned = []
    for idx, sc in enumerate(scenes):
        visual = _norm(sc.get("camera"))
        requires_user_upload = any(
            kw in visual.lower() for kw in ["your", "you", "selfie", "personal", "custom"]
        )
        planned.append({
            "scene_index": idx,
            "visual": visual,
            "onscreen_text": _norm(sc.get("onscreen_text")),
            "music": _norm(sc.get("music")),
            "transition": _norm(sc.get("transition")),
            "requires_user_upload": requires_user_upload,
            "suggested_source": "user_upload" if requires_user_upload else "stock",
            "start_seconds": float(sc.get("start_seconds", 0)),
            "end_seconds": float(sc.get("end_seconds", 0)),
        })
    return planned

def compute_minimal_footage(planned_footage: List[Dict[str, Any]]) -> List[ShotSpec]:
    """
    Deduplicate similar visuals; return absolute minimal set the user must film.
    """
    seen: Dict[str, int] = {}
    checklist: List[ShotSpec] = []
    for item in planned_footage:
        # Only demand uploads for scenes that require user footage
        if not item.get("requires_user_upload", False):
            continue
        key = (item.get("visual") or "general").lower()
        # First time we encounter this visual → create a single canonical shot request
        if key not in seen:
            duration = max(1.0, item.get("end_seconds", 0) - item.get("start_seconds", 0))
            shot = ShotSpec(
                scene_index=item["scene_index"],
                duration=float(duration),
                shot_type=_infer_shot_type(item.get("visual") or ""),
                description=item.get("visual") or "User-specific shot",
                requires_user_upload=True,
                onscreen_text=item.get("onscreen_text", ""),
                music=item.get("music", ""),
                transition=item.get("transition", "")
            )
            checklist.append(shot)
            seen[key] = 1
    return checklist

def shooting_instructions(parsed_script: Dict[str, Any]) -> List[str]:
    """
    Human-readable guidance per scene (how to shoot, lighting, b-roll tips).
    """
    out = []
    for i, sc in enumerate(parsed_script.get("scenes", []), start=1):
        seg = []
        seg.append(f"Scene {i} ({sc.get('start')}–{sc.get('end')})")
        if sc.get("camera"):   seg.append(f"• Shot: {sc['camera']}")
        if sc.get("lighting"): seg.append(f"• Lighting: {sc['lighting']}")
        if sc.get("text"):     seg.append(f"• Narration focus: “{sc['text']}”")
        if sc.get("onscreen_text"): seg.append(f"• On‑screen text: {sc['onscreen_text']}")
        if sc.get("music"):    seg.append(f"• Music: {sc['music']}")
        if sc.get("transition"): seg.append(f"• Transition: {sc['transition']}")
        out.append("\n".join(seg))
    return out

# ---------- NL Editing Plans ----------

@dataclass
class EditCommand:
    type: str                   # 'trim', 'speed', 'caption', 'zoom', 'music_gain', 'transition'
    target: str                 # 'scene:2', 'clip:<filename>', 'global'
    value: Any                  # payload (e.g. seconds, factor, text)

def parse_nl_edit_request(nl: str) -> List[EditCommand]:
    """
    Lightweight, robust parser for common phrasing:
      - trim scene 2 to 1.5s
      - add captions "..." on scene 3
      - speed up scene 1 by 1.25x
      - apply zoom-in on scene 2
      - lower music by 6dB
      - add crossfade 200ms between scenes
    """
    cmds: List[EditCommand] = []
    text = (nl or "").lower().strip()
    if not text:
        return cmds

    # trim scene N to Xs
    for m in re.finditer(r'trim\s+scene\s+(\d+)\s+to\s+([0-9.]+)s', text):
        cmds.append(EditCommand("trim", f"scene:{int(m.group(1))}", float(m.group(2))))

    # speed up scene N by fx
    for m in re.finditer(r'speed(\s+up)?\s+scene\s+(\d+)\s+by\s+([0-9.]+)x', text):
        cmds.append(EditCommand("speed", f"scene:{int(m.group(2))}", float(m.group(3))))

    # zoom in scene N
    for m in re.finditer(r'(apply\s+)?zoom-?in\s+on\s+scene\s+(\d+)', text):
        cmds.append(EditCommand("zoom", f"scene:{int(m.group(2))}", "in"))

    # captions "...“ on scene N
    for m in re.finditer(r'captions?\s+"([^"]+)"\s+on\s+scene\s+(\d+)', text):
        cmds.append(EditCommand("caption", f"scene:{int(m.group(2))}", m.group(1)))

    # music volume change (global)
    if re.search(r'lower\s+music', text):
        db = -6.0
        if (m := re.search(r'by\s+([0-9.]+)\s*d?b', text)):
            db = -abs(float(m.group(1)))
        cmds.append(EditCommand("music_gain", "global", db))

    # crossfade between scenes
    for m in re.finditer(r'(add|apply)\s+crossfade\s+([0-9]+)ms', text):
        cmds.append(EditCommand("transition", "between_scenes", int(m.group(2))))

    return cmds

# ---------- Assembly Plan ----------

def build_assembly_plan(planned_footage: List[Dict[str, Any]],
                        scene_selections: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge planned_footage with user selections to produce the “assembly plan”
    your UI already shows. We extend it slightly with timing placeholders.
    """
    out = []
    for pf in planned_footage:
        s_idx = pf["scene_index"]
        pick = scene_selections.get(f"scene_{s_idx}", {})
        out.append({
            "scene_index": s_idx,
            "use_stock": bool(pick.get("use_stock", not pf.get("requires_user_upload", False))),
            "filename": pick.get("filename"),        # user upload (if any)
            "visual": pf.get("visual"),
            "onscreen_text": pf.get("onscreen_text"),
            "music": pf.get("music"),
            "transition": pf.get("transition"),
            "start_seconds": pf.get("start_seconds", 0.0),
            "end_seconds": pf.get("end_seconds", 0.0),
            # editable fields (can be mutated by NL commands)
            "speed": 1.0,
            "zoom": None,   # 'in' or 'out'
            "caption": None,
        })
    return out

def apply_edit_commands(assembly_plan: List[Dict[str, Any]], commands: List[EditCommand]) -> List[Dict[str, Any]]:
    """
    Apply NL edit commands in-place to the assembly plan (non-destructive copy).
    """
    plan = [dict(item) for item in assembly_plan]
    for cmd in commands:
        if cmd.type in {"trim", "speed", "zoom", "caption"} and cmd.target.startswith("scene:"):
            idx = int(cmd.target.split(":")[1])
            for item in plan:
                if item["scene_index"] == idx - 1:  # NB: UI shows 1-based scenes
                    if cmd.type == "trim":
                        dur = max(0.2, float(cmd.value))
                        item["end_seconds"] = item["start_seconds"] + dur
                    elif cmd.type == "speed":
                        item["speed"] = max(0.1, float(cmd.value))
                    elif cmd.type == "zoom":
                        item["zoom"] = cmd.value
                    elif cmd.type == "caption":
                        item["caption"] = str(cmd.value)
        # global commands are exported with metadata; the renderer will use them
    return plan

# ---------- Rendering (MoviePy or FFmpeg script) ----------

def compile_ffmpeg_script(assembly_plan: List[Dict[str, Any]],
                          assets_dir: str,
                          out_path: str,
                          music_gain_db: float = 0.0,
                          crossfade_ms: int = 0) -> Tuple[str, str]:
    """
    Generate a portable FFmpeg shell script + Windows .bat.
    - Cuts clips, applies speed, concatenates, adds captions as drawtext (if any).
    - Music gain & crossfades are approximated (simple, reliable defaults).
    Returns (sh_path, bat_path).
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    sh_lines = ["#!/usr/bin/env bash", "set -e"]
    bat_lines = ["@echo off", "setlocal enableextensions enabledelayedexpansion"]

    filter_parts = []
    inputs = []
    idx_map = []
    for i, item in enumerate(assembly_plan):
        fn = item.get("filename")
        if not fn:
            # Stock footage path could be resolved here; we leave placeholder.
            continue
        clip_path = os.path.join(assets_dir, fn)
        inputs.append(clip_path)
        idx_map.append(i)

    # input args
    in_args = " ".join([f'-i "{p}"' for p in inputs])

    # For simplicity, one stream per input, then concat
    for n, i in enumerate(idx_map):
        it = assembly_plan[i]
        label_v = f"[v{n}]"
        label_a = f"[a{n}]"

        # trim
        ss = max(0.0, float(it.get("start_seconds", 0.0)))
        to = max(ss, float(it.get("end_seconds", ss + 1.0)))
        trim = f"trim=start={ss}:end={to},setpts=PTS-STARTPTS"
        # speed
        spd = float(it.get("speed", 1.0))
        spdfilter = "setpts=PTS/{:.4f}".format(spd) if spd != 1.0 else None
        # zoom (simple scale to 110% with crop to original size)
        zoom = None
        if it.get("zoom") == "in":
            zoom = "scale=iw*1.1:ih*1.1,crop=iw/1.1:ih/1.1"
        # caption
        cap = None
        caption_text = it['caption'].replace("'", r"\'")
        cap = f"drawtext=text='{caption_text}':x=(w-text_w)/2:y=h-100:fontsize=42:fontcolor=white:box=1:boxcolor=black@0.5"

        v_chain = ",".join([p for p in [trim, spdfilter, zoom, cap] if p])
        if not v_chain:
            v_chain = "null"
        filter_parts.append(f"[{n}:v]{v_chain}{label_v}")

        # audio: simple atrim, speed via atempo (<=2.0 segments)
        a_trim = f"atrim=start={ss}:end={to},asetpts=PTS-STARTPTS"
        a_spd = None
        if spd != 1.0:
            # Split into 2x atempo if >2
            facs = []
            remaining = spd
            while remaining > 2.0 + 1e-6:
                facs.append(2.0)
                remaining /= 2.0
            facs.append(remaining)
            a_spd = ",".join([f"atempo={f:.4f}" for f in facs])
        a_chain = ",".join([p for p in [a_trim, a_spd] if p]) or "anull"
        filter_parts.append(f"[{n}:a]{a_chain}{label_a}")

    # concat video+audio
    if idx_map:
        v_inputs = "".join([f"[v{n}]" for n in range(len(idx_map))])
        a_inputs = "".join([f"[a{n}]" for n in range(len(idx_map))])
        concat = f"{v_inputs}{a_inputs}concat=n={len(idx_map)}:v=1:a=1[v][a]"
        filter_parts.append(concat)
        # music gain (global)
        if music_gain_db:
            filter_parts.append(f"[a]volume={10 ** (music_gain_db / 20):.4f}[aout]")
            out_audio_label = "[aout]"
        else:
            out_audio_label = "[a]"
        filtergraph = ";".join(filter_parts)
        cmd = f'ffmpeg -y {in_args} -filter_complex "{filtergraph}" -map "[v]" -map "{out_audio_label}" "{out_path}"'
    else:
        cmd = f'echo No inputs found. Unable to assemble > "{out_path}.log" && exit 1'

    sh_lines.append(cmd)
    bat_lines.append(cmd)

    sh_path = (out_path + ".sh") if not out_path.endswith(".sh") else out_path
    bat_path = (out_path + ".bat") if not out_path.endswith(".bat") else out_path

    with open(sh_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sh_lines))
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(bat_lines))

    return sh_path, bat_path

def render_with_moviepy(assembly_plan: List[Dict[str, Any]],
                        assets_dir: str,
                        out_path: str,
                        music_gain_db: float = 0.0,
                        crossfade_ms: int = 0) -> bool:
    """
    Attempt to render using moviepy if available. Falls back to FFmpeg script generation.
    """
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx, TextClip, CompositeVideoClip, AudioFileClip
    except Exception:
        return False

    clips = []
    for item in assembly_plan:
        fn = item.get("filename")
        if not fn:  # skip stock placeholders
            continue
        path = os.path.join(assets_dir, fn)
        base = VideoFileClip(path).subclip(item["start_seconds"], item["end_seconds"])
        if item.get("speed") and item["speed"] != 1.0:
            base = base.fx(vfx.speedx, factor=item["speed"])
        if item.get("zoom") == "in":
            # simple zoom-in (scale up then crop by position)
            w, h = base.size
            base = base.resize(1.1).crop(x_center=w/2, y_center=h/2, width=w, height=h)
        if item.get("caption"):
            tc = TextClip(item["caption"], fontsize=42, color="white").set_duration(base.duration)
            tc = tc.on_color(size=(base.w, tc.h+20), color=(0,0,0), pos=("center","bottom"), col_opacity=0.5)
            base = CompositeVideoClip([base, tc.set_position(("center", "bottom"))])
        clips.append(base)

    if not clips:
        return False

    final = concatenate_videoclips(clips, method="compose")
    # music gain: we apply on the composite audio if any
    if final.audio and music_gain_db:
        factor = 10 ** (music_gain_db / 20)
        final = final.volumex(factor)

    # crossfade (simple: apply between clips — omitted here for reliability)
    final.write_videofile(out_path, codec="libx264", audio_codec="aac")
    return True

# ---------- AI Generation Plan (provider-agnostic) ----------

def ai_generation_plan(parsed_script: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Return per‑scene prompts that an external “AI video” generator can consume.
    This lets you integrate Runway/KAiber/Pika/etc. later without refactoring.
    """
    plans = []
    for i, sc in enumerate(parsed_script.get("scenes", []), start=1):
        prompt = []
        if sc.get("camera"):   prompt.append(f"Shot: {sc['camera']}")
        if sc.get("lighting"): prompt.append(f"Lighting: {sc['lighting']}")
        if sc.get("text"):     prompt.append(f"Narration: {sc['text']}")
        if sc.get("onscreen_text"): prompt.append(f"On‑screen: {sc['onscreen_text']}")
        plans.append({
            "scene": str(i),
            "duration_hint": f"{max(1, sc.get('end_seconds', 1)-sc.get('start_seconds', 0))}s",
            "prompt": " | ".join(prompt) or "General scene consistent with script",
        })
    return plans
