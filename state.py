"""State persistence for the Sketchman pipeline.

GitHub Actions runners are ephemeral, so state.json would be lost every run.
Three complementary stores, all restored before a run and all written after:
  * git-committed copy (repo root: state.json)       -> always available
  * GitHub Actions cache  (work/.state.cache.json, via actions/cache)
  * In-memory fallback (last resort, per-process)
They are merged with max-timestamp semantics, so the fresher copy wins
field-by-field. Used for:
  * the 1-upload-per-day quota guard,
  * per-run history (what went out today, links),
  * last-used topic indexes (rotation de-dup),
  * quota tracking (1600 units/upload + 1 for verify, 10000 daily limit).
Never stores secrets.
"""
import json
import os
import threading
from typing import Any, Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
CACHE_FILE = os.path.join(HERE, "work", ".state.cache.json")

DEFAULT = {
    "version": 1,
    "updated": None,           # ISO timestamp of last write
    "last_upload": {"long": None, "short": None},   # YYYY-MM-DD per format
    "last_topics": {"long": None, "short": None},   # topic index per format
    "history": {},             # {YYYY-MM-DD: {"long": key|None, "short": key|None}}
    "links": {},               # {YYYY-MM-DD: {"long": url|None, "short": url|None}}
    "quota_used": 0,           # quota units used today (1600 per upload + 1 for verify)
    "quota_date": None,        # YYYY-MM-DD when quota_used was last reset
}

# Thread-local in-memory fallback for when both stores fail
_local_state = threading.local()


def _read(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _write_atomic(path: str, data: Dict[str, Any]) -> bool:
    """Write JSON atomically using temp file + rename."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp_path, path)
        return True
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return False


def load() -> Dict[str, Any]:
    """Merge git copy + cache copy + memory fallback (newest timestamp wins)."""
    merged = json.loads(json.dumps(DEFAULT))
    stores = []
    
    # Read from all sources
    for path in (STATE_FILE, CACHE_FILE):
        data = _read(path)
        if data:
            stores.append(data)
    
    # Check thread-local memory fallback
    if hasattr(_local_state, "data") and _local_state.data:
        stores.append(_local_state.data)
    
    if stores:
        # Sort by updated timestamp (newest last)
        stores.sort(key=lambda s: s.get("updated") or "")
        base = stores[-1]
        merged.update(base)
        
        # Union merge for dict fields (newest non-None value wins per key)
        for k in ("history", "links", "last_upload", "last_topics"):
            merged[k] = _union_dicts([s.get(k) or {} for s in stores])
    
    return merged


def _union_dicts(dicts: list) -> Dict[str, Any]:
    """Merge list of dicts. Last store with non-None value wins per key."""
    out = {}
    for d in dicts:
        for k, v in d.items():
            if v is not None:
                out[k] = v
    return out


def save(state: Dict[str, Any]) -> bool:
    """Save to all available stores. Returns True if at least one succeeded."""
    state["updated"] = _now_iso()
    success = False
    
    for path in (STATE_FILE, CACHE_FILE):
        if _write_atomic(path, state):
            success = True
    
    # Always update memory fallback
    _local_state.data = json.loads(json.dumps(state))
    success = True
    
    return success


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def _reset_quota_if_new_day(state: Dict[str, Any]) -> Dict[str, Any]:
    """Reset quota counter if it's a new day."""
    today = _today()
    if state.get("quota_date") != today:
        state["quota_used"] = 0
        state["quota_date"] = today
    return state


def already_uploaded(fmt: str) -> bool:
    """True if this format already went out today (1/day guard)."""
    return state_last_upload(fmt) == _today()


def state_last_upload(fmt: str) -> Optional[str]:
    return load()["last_upload"].get(fmt)


def quota_remaining() -> int:
    """Return remaining quota units for today (default 10000)."""
    st = load()
    _reset_quota_if_new_day(st)
    return max(0, 10000 - st.get("quota_used", 0))


def can_upload(quota_cost: int = 1600) -> bool:
    """Check if we have enough quota for an upload."""
    return quota_remaining() >= quota_cost


def record_quota_usage(cost: int) -> None:
    """Record quota usage."""
    st = load()
    _reset_quota_if_new_day(st)
    st["quota_used"] = st.get("quota_used", 0) + cost
    save(st)


def record_upload(fmt: str, topic_key: str, link: Optional[str] = None) -> Dict[str, Any]:
    """Record a successful upload. Returns the updated dict."""
    st = load()
    today = _today()
    st["last_upload"][fmt] = today
    if topic_key:
        st["last_topics"][fmt] = topic_key
    st["history"].setdefault(today, {})[fmt] = topic_key
    if link:
        st["links"].setdefault(today, {})[fmt] = link
    # Track quota: ~1600 units per upload + 1 for verify
    st["quota_used"] = st.get("quota_used", 0) + 1600
    st["quota_date"] = today
    save(st)
    return st


def summary() -> str:
    """Human-readable one-liner for logs/alerts."""
    st = load()
    h = st.get("history") or {}
    rows = []
    for day in sorted(h):
        for fmt, key in sorted(h[day].items()):
            link = (st.get("links") or {}).get(day, {}).get(fmt)
            rows.append(f"{day} {fmt}: {key} {link or ''}".strip())
    if not rows:
        return "no upload history yet (state.json fresh)"
    return "; ".join(rows)


def reset_for_testing() -> None:
    """Reset state for testing purposes."""
    global _local_state
    _local_state.data = None
    for path in (STATE_FILE, CACHE_FILE):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "record":
        fmt = sys.argv[2] if len(sys.argv) > 2 else "short"
        key = sys.argv[3] if len(sys.argv) > 3 else "manual"
        link = sys.argv[4] if len(sys.argv) > 4 else None
        record_upload(fmt, key, link)
        print("recorded.")
    elif len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_for_testing()
        print("reset.")
    else:
        print(json.dumps(load(), indent=2, sort_keys=True))
        print(summary())