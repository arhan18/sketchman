"""Script files: the content source of truth for v3.

A script is one JSON file under scripts/<series>/<slug>.json:

    {
      "series": "arjun",
      "format": "long" | "short",
      "title": "Why Your Salary Is a Trap",
      "description": "YouTube description",
      "tags": "comma, separated, tags",
      "thumbnail": {"headline": "...", "scene": "numbers", "props": {...}},
      "shots": [
        {"scene": "establish", "props": {...}, "narr": "One or two sentences."}
      ]
    }

`narr` is split into sentences at build time, and each sentence becomes one
clip: one TTS call, one measured duration, one burned-in caption. The visual
stays on for the whole shot while the caption changes per sentence, which is
how the reference channels read.
"""
import glob
import json
import os
import re
from typing import Any, Dict, List, Optional

import series as series_mod

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(HERE, "scripts")

REQUIRED = ("series", "format", "title", "shots")
SHOT_FIELDS = ("scene", "narr")


def split_sentences(text: str) -> List[str]:
    """Split narration into caption-sized sentences."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def load(path: str) -> Dict[str, Any]:
    with open(path) as f:
        script = json.load(f)
    missing = [k for k in REQUIRED if k not in script]
    if missing:
        raise ValueError(f"{os.path.basename(path)}: missing {missing}")
    if script["series"] not in series_mod.SERIES:
        raise ValueError(f"{os.path.basename(path)}: unknown series {script['series']}")
    if not script["shots"]:
        raise ValueError(f"{os.path.basename(path)}: no shots")
    for i, shot in enumerate(script["shots"]):
        for field in SHOT_FIELDS:
            if not shot.get(field):
                raise ValueError(f"{os.path.basename(path)}: shot {i} missing {field}")
    return script


def key(script: Dict[str, Any], path: str) -> str:
    """Stable rotation key, e.g. arjun/quiet-ledger."""
    return f"{script['series']}/{os.path.splitext(os.path.basename(path))[0]}"


def all_scripts(fmt: Optional[str] = None) -> List[Dict[str, Any]]:
    """Every script, series-rotation first, then slug, deterministically."""
    order = {sid: i for i, sid in enumerate(series_mod.ROTATION)}
    out = []
    for path in glob.glob(os.path.join(SCRIPTS_DIR, "*", "*.json")):
        script = load(path)
        if fmt and script["format"] != fmt:
            continue
        script["_path"] = path
        script["_key"] = key(script, path)
        out.append(script)
    out.sort(key=lambda s: (order[s["series"]], os.path.basename(s["_path"])))
    return out


def pick(fmt: str, topic_override: Optional[str] = None) -> Dict[str, Any]:
    """Next script in rotation, using state so we never repeat back to back."""
    pool = all_scripts(fmt)
    if not pool:
        raise ValueError(f"no {fmt} scripts found under {SCRIPTS_DIR}")
    keys = [s["_key"] for s in pool]
    if topic_override:
        for script in pool:
            if topic_override in (script["_key"], os.path.basename(script["_key"])):
                return script
        raise ValueError(f"unknown script override {topic_override}")
    try:
        import state
        last = state.load().get("last_topics", {}).get(fmt)
    except Exception:
        last = None
    if last in keys:
        return pool[(keys.index(last) + 1) % len(pool)]
    import datetime as dt
    return pool[dt.date.today().toordinal() % len(pool)]


def clips(script: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Expand shots into sentence-level clips (durations filled in later).

    Each clip carries `variant` (which sentence of its shot it is) and
    `shot_index`, so the renderer can keep moving the camera instead of
    holding one frozen frame while the caption changes.
    """
    out: List[Dict[str, Any]] = []
    for shot_index, shot in enumerate(script["shots"]):
        for variant, sentence in enumerate(split_sentences(shot["narr"])):
            out.append({
                "scene": shot["scene"],
                "props": shot.get("props", {}),
                "caption": sentence,
                "narr": sentence,
                "variant": variant,
                "shot_index": shot_index,
                "character": shot.get("character"),
            })
    return out


def check_variety(script: Dict[str, Any]) -> List[str]:
    """Complain about repeated visuals so episodes never look like a loop.

    A shot may hold for several sentences (that is fine), but two shots with
    the same scene AND the same props anywhere in one episode is a repeat.
    """
    seen = {}
    problems = []
    for i, shot in enumerate(script["shots"]):
        key = (shot["scene"], json.dumps(shot.get("props", {}), sort_keys=True))
        if key in seen:
            problems.append(
                f"shots {seen[key]} and {i} render the identical visual "
                f"({shot['scene']}); change the props or the scene")
        seen.setdefault(key, i)
    return problems


def word_count(script: Dict[str, Any]) -> int:
    return sum(len(shot["narr"].split()) for shot in script["shots"])


if __name__ == "__main__":
    import sys
    fmt = sys.argv[1] if len(sys.argv) > 1 else None
    for script in all_scripts(fmt):
        print(f"{script['_key']:34s} {script['format']:5s} "
              f"{word_count(script):5d} words  {len(clips(script)):4d} clips")
