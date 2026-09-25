"""Self-check for the v3 pipeline. No framework: python3 tests/test_core.py

Covers the pure logic that would otherwise fail silently in CI: series
rotation, script validation, sentence-to-clip expansion, clip timing, and the
per-host voice map.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import renderer
import script as script_mod
import series as series_mod
import voice


def test_series_rotation():
    assert series_mod.all_series() == ["arjun", "mira", "kabir"]
    assert series_mod.next_in_rotation("kabir") == "arjun"
    assert series_mod.get("mira").host == "Mira"
    assert series_mod.get("nope").id == "arjun", "unknown ids fall back, never crash"
    assert series_mod.SERIES["kabir"].background.startswith("#")


def test_voice_profiles():
    for sid in series_mod.all_series():
        prof = voice._profile(sid)
        assert prof["kokoro"] and prof["edge"] and prof["edge_rate"]
    assert voice._profile("mira")["edge"] == "en-US-AriaNeural"
    assert all("en-IN" not in v["edge"] for v in voice.VOICE_PROFILES.values())
    assert voice.HOUSE_BASE == "en-us"
    assert voice._profile(None) == voice._profile("default")


def test_scripts_load_and_validate():
    longs = script_mod.all_scripts("long")
    shorts = script_mod.all_scripts("short")
    assert len(longs) == 3, f"expected one long per series, got {len(longs)}"
    assert len(shorts) == 3, f"expected one short per series, got {len(shorts)}"
    assert {s["series"] for s in longs} == set(series_mod.all_series())
    # rotation order, not alphabetical
    assert [s["series"] for s in longs] == series_mod.all_series()
    for s in longs:
        assert 800 <= script_mod.word_count(s) <= 1700, (
            f"{s['_key']} is {script_mod.word_count(s)} words, want 800-1700")


def test_bad_script_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "bad.json")
        with open(path, "w") as f:
            json.dump({"series": "nobody", "format": "long", "title": "x",
                       "shots": [{"scene": "numbers", "narr": "Hi."}]}, f)
        try:
            script_mod.load(path)
        except ValueError as e:
            assert "unknown series" in str(e)
        else:
            raise AssertionError("unknown series should be rejected")


def test_clips_and_timing():
    s = {"shots": [{"scene": "numbers", "narr": "One. Two! Three?",
                    "props": {"value": "3"}}]}
    clips = script_mod.clips(s)
    assert len(clips) == 3
    assert clips[0]["caption"] == "One."
    assert clips[2]["props"] == {"value": "3"}
    timed = renderer.with_timing([{"duration": 2.0}, {"duration": 1.5}])
    assert timed[0]["start"] == 0.0 and timed[0]["end"] == 2.0
    assert timed[1]["start"] == 2.0 and timed[1]["end"] == 3.5


def test_pick_never_repeats_back_to_back():
    first = script_mod.pick("long")
    keys = [s["_key"] for s in script_mod.all_scripts("long")]
    nxt = keys[(keys.index(first["_key"]) + 1) % len(keys)]
    import state
    before = state.load()
    try:
        after = state.load()
        after["last_topics"] = {"long": first["_key"]}
        state.save(after)
        assert script_mod.pick("long")["_key"] == nxt
    finally:
        state.save(before)


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except Exception as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    print("all good" if not failures else f"{failures} failing")
    sys.exit(1 if failures else 0)
