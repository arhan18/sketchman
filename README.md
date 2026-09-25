# Sketchman — multi-series finance video factory (v3)

Original finance stories for the **Fiscalore** channel, built from JSON scripts
and rendered as per-series animated scenes in headless Chromium, voiced per
host, and uploaded to YouTube by GitHub Actions.

## The three series

| Id | Host / show | Visual style | Voice (Kokoro → Edge fallback) |
|---|---|---|---|
| `arjun` | Arjun — The Quiet Ledger | clean educational (cream, green, diagram-led) | `am_adam` → `en-IN-PrabhatNeural` |
| `mira` | Mira — Myth Busters | minimal metaphor (huge negative space, one object) | `af_bella` → `en-IN-NeerjaNeural` |
| `kabir` | Kabir — The Wealth Lab | cinematic story (night, gold key light, depth) | `am_michael` → `en-IN-PrabhatNeural` |

Every definition lives in `series.py`; scenes per style live in `scenes/`.

## Schedule (2 long + 2 short / week)

| Day (UTC 04:30 = 10:00 IST) | What |
|---|---|
| Mon / Thu | LONG (8–10 min, 1280×720) |
| Tue / Fri | SHORT (30–60 s, 720×1280) |
| Sat / Sun | rest |

Longs and shorts round-robin across the three series using `state.json`, so
each host gets airtime and no script repeats back to back.

## How a build works

1. `script.pick()` chooses the next script in rotation.
2. Each shot's `narr` is split into sentences; every sentence becomes one clip
   with one TTS call (Kokoro local, Edge fallback) and one measured duration.
3. `renderer.render()` builds one self-contained HTML page per video (style
   template + payload) and captures frames in headless Chromium, piping PNG
   bytes straight into ffmpeg — no PNG pile on disk. `window.seek(t)` pauses
   every CSS animation at an explicit time, so frames are deterministic.
4. Captions are the spoken sentences themselves, burned in, so text and audio
   can never drift apart.
5. `latest.json` points the uploader at the new video, meta and thumbnail.

## Scripts

`scripts/<series>/<slug>.json`:

```json
{
  "series": "arjun",
  "format": "long",
  "title": "Payday Is a Trap: The 24-Hour Rule",
  "description": "...", "tags": "...",
  "thumbnail": {"headline": "...", "scene": "numbers", "props": {}},
  "shots": [{"scene": "establish", "props": {}, "narr": "One or two sentences."}]
}
```

Scene kinds: `establish`, `numbers`, `object`, `split`, `chart`, `timeline`,
`endcard`. Each style renders all seven; only the look differs.

Check the library and word counts:

```bash
python3 script.py            # all scripts
python3 script.py long       # one format
```

## Local run

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
python3 generate.py --format long                    # next in rotation
python3 generate.py --format short --script mira/emergency-fund-myth
DRY_RUN=1 python3 upload.py --short                 # prints, uploads nothing
python3 tests/test_core.py                          # pipeline self-check
```

ffmpeg is resolved by `binpath.py`: env override → project-local arm64 build
under `tools/node/node_modules` → PATH. If the system ffmpeg is an unusable
x86_64 binary (common on Apple Silicon), install a local one:

```bash
npm install --prefix tools/node @ffmpeg-installer/ffmpeg @ffprobe-installer/ffprobe
```

## Files

- `series.py` — the three series (palette, style, sign-off, rotation)
- `script.py` — script loading, validation, sentence→clip expansion, rotation
- `scenes/*.html` — per-style scene templates (educational / metaphor / cinematic)
- `scenes/runtime.js`, `scenes/base.css` — deterministic seek + shared stage
- `renderer.py` — Chromium frame capture, ffmpeg piping, audio concat, stills
- `voice.py` — per-host voices, normalization, Kokoro→Edge fallback + timeout
- `generate.py` — one build: pick script → narrate → render → thumbnail → manifest
- `upload.py` — YouTube Data API upload (`--verify`, `--short`, `DRY_RUN=1`)
- `state.py` — rotation, daily quota, upload history (git + cache + memory)
- `binpath.py` — ffmpeg/ffprobe resolution

## Re-auth

See `README-REAUTH.md`. Tokens are production-mode (consent screen published),
so they do not expire on the 7-day testing clock. If a token ever dies:
`python3 reauth.py`, then `gh secret set YOUTUBE_REFRESH_TOKEN < rt.bin.json`.
