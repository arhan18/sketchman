"""State persistence for the Sketchman pipeline.

GitHub Actions runners are ephemeral, so state.json would be lost every run.
Two complementary stores, both restored before a run and both written after:
  * git-committed copy (repo root: state.json)   -> always available
  * GitHub Actions cache  (work/.state.cache.json, via actions/cache)
They are merged with max-timestamp semantics, so the fresher copy wins
field-by-field. Used for:
  * the 1-upload-per-day quota guard,
  * per-run history (what went out today, links),
  * last-used topic indexes (rotation de-dup).
Never stores secrets.
"""
import json
import os

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
}


def _read(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load():
    """Merge git copy + cache copy (cache wins on same timestamp), else defaults."""
    merged = json.loads(json.dumps(DEFAULT))
    stores = [s for s in (_read(STATE_FILE), _read(CACHE_FILE)) if s]
    if stores:
        stores.sort(key=lambda s: s.get("updated") or "")
        base = stores[-1]  # highest updated
        merged.update(base)
        # merge history/links/last_upload/last_topics union-style
        for k in ("history", "links"):
            merged[k] = _union_dicts([s.get(k) or {} for s in stores])
        for k in ("last_upload", "last_topics"):
            merged[k] = _union_dicts([s.get(k) or {} for s in stores],
                                     newest=True)
    return merged


def _union_dicts(dicts, newest=False):
    """Merge list of dicts. newest=True -> per-key comparison of stored ISO
    timestamps is not possible (plain values), so last store wins per key."""
    out = {}
    for d in dicts:
        for k, v in d.items():
            if k not in out or v is not None:
                out[k] = v
    return out


def save(state):
    state["updated"] = _now_iso()
    for path in (STATE_FILE, CACHE_FILE):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(state, f, indent=2, sort_keys=True)


def _now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def already_uploaded(fmt):
    """True if this format already went out today (1/day guard)."""
    return state_last_upload(fmt) == _today()


def state_last_upload(fmt):
    return load()["last_upload"].get(fmt)


def record_upload(fmt, topic_key, link=None):
    """Record a successful upload. Returns the updated dict."""
    st = load()
    today = _today()
    st["last_upload"][fmt] = today
    if topic_key:
        st["last_topics"][fmt] = topic_key
    st["history"].setdefault(today, {})[fmt] = topic_key
    if link:
        st["links"].setdefault(today, {})[fmt] = link
    save(st)
    return st


def summary():
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "record":
        fmt = sys.argv[2] if len(sys.argv) > 2 else "short"
        key = sys.argv[3] if len(sys.argv) > 3 else "manual"
        link = sys.argv[4] if len(sys.argv) > 4 else None
        record_upload(fmt, key, link)
        print("recorded.")
    else:
        print(json.dumps(load(), indent=2, sort_keys=True))
        print(summary())