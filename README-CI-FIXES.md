# CI Fixes — Why runs failed & what changed (Oct 2026)

## Root cause of Sep 29 – Oct 15 failures

**Disk space exhaustion on GitHub-hosted runners.**

The OpenVoice house voice setup downloads:
- PyTorch wheels (~1.5 GB)
- MeloTTS + OpenVoice checkpoints (~320 MB)
- NLTK data packages (~100 MB)

Total cached footprint: **~3.6 GB** (`voice-openvoice/` + `~/.cache/pip/`).

GitHub-hosted `ubuntu-latest` runners provide ~14 GB free. After:
- Python + Playwright + system deps (~4 GB)
- Actions cache restore overhead
- OpenVoice cache restore (~3.6 GB)

…the runner hit **< 20 MB free** and `pip install` failed with `OSError: [Errno 28] No space left on device`.

## What this patch does

1. **Default VOICE_ENGINE switched to `kokoro`** (lightweight, local, ~200 MB cached).
   - Kokoro-82M runs entirely on-device via ONNX Runtime.
   - No PyTorch, no 300+ MB checkpoints, no NLTK downloads.
   - Still sounds human; am_adam @ 0.93 speed ≈ calm male storyteller.

2. **Aggressive pre-install disk cleanup** step:
   - Removes .NET, GHC, CodeQL toolcaches (~3 GB)
   - Clears apt & pip caches
   - Runs **before** any heavy installs.

3. **OpenVoice setup made optional + continue-on-error**:
   - Only runs if `VOICE_ENGINE=openvoice` is explicitly set.
   - On CI we use Kokoro; OpenVoice is for local high-quality renders.
   - If it fails (disk, network, missing HF token), the job continues and falls back.

4. **Failure alert now catches "No space left on device"**.

## Required GitHub Secrets (repo → Settings → Secrets → Actions)

| Secret | Required? | Purpose |
|--------|-----------|---------|
| `YOUTUBE_CLIENT_ID` | **YES** | OAuth client ID (Desktop app type) |
| `YOUTUBE_CLIENT_SECRET` | **YES** | OAuth client secret |
| `YOUTUBE_REFRESH_TOKEN` | **YES** | Mint via `python reauth.py` (see below) |
| `ALERT_SMTP_USER` | No | Gmail address for email alerts |
| `ALERT_SMTP_APP_PASSWORD` | No | 16-char Gmail App Password |
| `ALERT_SMTP_TO` | No | Override alert destination (default: SMTP_USER) |
| `ALERT_DISCORD_WEBHOOK` | No | Discord channel webhook URL |
| `ALERT_SLACK_WEBHOOK` | No | Slack incoming webhook URL |

**Without the three YouTube secrets the workflow cannot upload.**
Alert secrets are optional; GitHub emails the repo owner on failure anyway.

## One-time OAuth re-auth (if refresh token is dead)

```bash
cd sketchman
export YOUTUBE_CLIENT_ID="....apps.googleusercontent.com"
export YOUTUBE_CLIENT_SECRET="GOCSPX-...."
pip install google-auth-oauthlib google-api-python-client
python reauth.py
# → Browser opens. YOU approve the Google consent screen.
# → Prints: gh secret set YOUTUBE_REFRESH_TOKEN < /abs/path/rt.bin.json
# → Run that command, then: rm /abs/path/rt.bin.json
```

**Critical:** In Google Cloud Console → APIs & Services → OAuth consent screen,
ensure **Publishing status = "In production"**.
If it says "Testing", refresh tokens expire after ~7 days — the classic
`invalid_grant` loop.

## Verify locally (no upload, 1 quota unit)

```bash
DRY_RUN=1 python upload.py --verify
# [ok] verify: channel 'YourChannel' (subs=...)
```

## Schedule (UTC → IST)

| Day (UTC) | Cron | Format | IST time |
|-----------|------|--------|----------|
| Mon / Thu | 04:30 | long (16:9) | 10:00 |
| Tue / Fri | 04:30 | short (9:16) | 10:00 |
| Sat / Sun | — | rest | — |

Manual trigger: Actions → daily-sketchman → Run workflow → pick format/force.

## Local high-quality renders (OpenVoice)

```bash
export VOICE_ENGINE=openvoice
# Ensure voice-openvoice/ checkpoints exist (ci/setup-voice.sh does this)
python generate.py --format long --script arjun/payday-trap
```

## What the automation now guarantees

- ✅ **1 upload/day max per format** (quota guard + state persistence)
- ✅ **Quota-aware** — fails fast if < 1600 units remain
- ✅ **Credential check first** — 1 quota unit, fails before render if token dead
- ✅ **State persists** — git-committed `state.json` + Actions cache (survives runner recycle)
- ✅ **Alerts on failure** — email/Discord/Slack (if secrets set)
- ✅ **Graceful TTS fallback** — Kokoro → Edge (no hard dependency on OpenVoice)
- ✅ **Disk-safe on CI** — cleanup step + lightweight default engine