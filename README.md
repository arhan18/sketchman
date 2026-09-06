# Sketchman — colored explainer video factory (v2)

Daily money-mindset videos (long 16:9 + shorts 9:16): colored flat-style
illustration scenes with slow zoom motion, natural voiceover, caption pills,
and bold hook thumbnails — rendered with PIL + ffmpeg, voiced with Edge TTS,
auto-uploaded to YouTube via GitHub Actions.

## Schedule (3 long + 3 short / week)

| Day (IST) | What |
|---|---|
| Mon / Wed / Fri 10:00 | LONG (~6–8 min, 1280×720) |
| Tue / Thu / Sat 10:00 | SHORT (~25–50 s, 720×1280) |
| Sun | rest |

## Setup (one time)

1. Create a **public GitHub repo** from this folder.
2. Add Actions secrets (repo Settings → Secrets → Actions):
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`
   - Get them from Google Cloud Console: enable **YouTube Data API v3**,
     create an OAuth Desktop client, then run a one-time OAuth flow to mint
     the refresh token (any `get_youtube_token.py`-style script works).
3. Manual run first: Actions → daily-sketchman → Run workflow → check the
   video on your channel before leaving the schedule on.

## Local test

```bash
pip install -r requirements.txt   # + ffmpeg on PATH
python generate.py --format short --topic 1
DRY_RUN=1 python upload.py short-1.mp4 short-1.json --short
```

## Quota notes

One upload ≈ 1,600 YouTube API units; default daily quota is 10,000.
One video/day is safe. Topics rotate via `state.json` (committed by local runs;
Actions runners start fresh each time — rotation state resets, so the queue
cycles deterministically; add more topics in `topics.py` to extend variety).

## Files

- `art.py` — colored flat illustration scenes (10 scenes)
- `voice.py` — natural voice + pronunciation normalization (Rs/₹/%/abbreviations)
- `thumbnails.py` — bold hook thumbnails (auto-uploaded with each video)
- `topics.py` — original money-mindset scripts (long + short queues)
- `generate.py` — TTS → Ken Burns scene motion → caption pills → mux + thumbnail
- `upload.py` — YouTube Data API upload (env creds, `--short`, `--private`, `--thumbnail`)
