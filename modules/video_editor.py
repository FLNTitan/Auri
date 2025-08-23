# modules/video_editor.py
import os
from typing import List, Dict, Any, Tuple
from .video import apply_edit_commands, parse_nl_edit_request, compile_ffmpeg_script, render_with_moviepy

def assemble_video(assembly_plan: List[Dict[str, Any]],
                   assets_dir: str,
                   out_path: str,
                   nl_edit_request: str = "",
                   music_gain_db: float = 0.0,
                   crossfade_ms: int = 0) -> Tuple[str, str]:
    """
    Apply NL edits → try moviepy → otherwise emit FFmpeg scripts and return paths.
    Returns (result_type, path)
      - ("file", out_path) if moviepy rendered
      - ("ffmpeg_script", sh_path) if script created
    """
    cmds = parse_nl_edit_request(nl_edit_request)
    edited_plan = apply_edit_commands(assembly_plan, cmds)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    # Try moviepy render
    ok = render_with_moviepy(edited_plan, assets_dir, out_path, music_gain_db, crossfade_ms)
    if ok:
        return ("file", out_path)

    # Fallback: create FFmpeg scripts
    sh_path, bat_path = compile_ffmpeg_script(edited_plan, assets_dir, out_path, music_gain_db, crossfade_ms)
    # Prefer returning sh; Windows users will see the .bat next to it
    return ("ffmpeg_script", sh_path)
