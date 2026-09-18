# Apply & run: the hardened Sketchman pipeline

Everything here was fixed and verified locally against the current repo.
The changes are reviewable as a single git commit + `git diff`.

## What changed (one-liners)

| File | Change |
|------|--------|
| `upload.py` | Rewritten: refresh-token diagnostics with re-auth pointer on `invalid_grant`, `--verify` cred check, retry/backoff for quota + 5xx + 429 (honors `Retry-After`), 1/day guard via `state.py`, resumable upload, non-fatal thumbnails |
| `reauth.py` | NEW: one-time OAuth walkthrough (loopback), verifies channel, prints `gh secret set` commands; never prints the token |
| `state.py` | NEW: state.json merged from git-committed copy + GH cache; 1/day guard, rotation + link history |
| `alerts.py` | NEW: Gmail SMTP failure email (app password); silently degrades → GitHub's built-in failure emails if unconfigured |
| `voice.py` | Resume-safe Kokoro model download (+retry); Kokoro → Edge fallback with one retry; loud failure if both fail |
| `art.py` | Fixed PIL-compat `pct()` (works on older Pillow, the "no drawings" crasher), shared `_base`, `ground_shadow`, enriched 7 near-empty scenes (coverage/color delta verified) |
| `generate.py` / `topics.py` | Kept existing per-sentence subtitle engine; stale `s_grind`/`s_intro` fallback fixed |
| `.github/workflows/daily.yml` | Cred verify → 1/day guard → render → upload → state git-commit + cache → email alert on failure |
| `requirements.txt` | + `google-auth-oauthlib` |

## Apply to the live repo

```bash
cd sketchman
git fetch origin && git checkout master     # get on the default branch
git diff origin/master..HEAD | git apply    # or: merge/push this branch
```

Practical path (you own the repo):

```bash
git add -A && git commit -m "ci: harden pipeline (OAuth diagnostics, quota guard, state persistence, email alerts)"
git push origin master
```

## Before the first scheduled run (one time)

1. **Re-auth once** — see `README-REAUTH.md`. 20 minutes, then it's hands-free.
   (If consent screen is in Testing mode, publish it there too.)
2. **Set/verify secrets** in the repo → Settings → Secrets → Actions:
   - `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`
   - Optional alerts (all three or none):
     - `ALERT_SMTP_USER` = your Gmail address
     - `ALERT_SMTP_APP_PASSWORD` = Gmail App Password (google.com/app-passwords)
     - `ALERT_SMTP_TO` = where alerts go (defaults to the user)
   - No `ALERT_SMTP_*` = GitHub emails you on failure automatically (fallback).
3. Enable the workflow if Actions were paused; the schedule is already set:
   - Mon/Wed/Fri 04:30 UTC → long (16:9)
   - Tue/Thu/Sat 04:30 UTC → short (9:16)
   - Never more than **1 upload/day** (hard guard, adjustable with the Force input).

## Verify the pipeline (no live upload)

```bash
# 1) credential check against your channel (1 quota unit)
export YOUTUBE_CLIENT_ID=... YOUTUBE_CLIENT_SECRET=... YOUTUBE_REFRESH_TOKEN=...
python upload.py --verify
# [ok] verify: channel '...' 

# 2) full render + TTS + thumb without uploading
python generate.py --format short --topic 1
DRY_RUN=1 python upload.py short-1.mp4 short-1.json --short
# [ok] DRY_RUN: would upload ...

# 3) state guard works
python state.py record short short-1 https://youtu.be/TEST
python upload.py --verify            # fine
DRY_RUN=1 python upload.py short-1.mp4 short-1.json --short
# after recording, a real upload attempt now says: already uploaded a short today (1/day guard)
python state.py | head                 # inspect merged history
```

## One-upload-per-day guard

- Runs use `state.py` → `state.json`, saved BOTH as a git commit and a GH
  cache entry, so the guard survives any runner.
- `workflow_dispatch` has a **Force** input to bypass it for intentional
  re-runs.
- Quota math: one upload ≈ **1,600 units** (video insert) + ~1 (verify). At
  6 videos/week the daily default quota (10,000) is nowhere near a limit; the
  guard exists so a retry-loop or double-run can never exceed it.

## If a run fails

1. GitHub emails you (zero-setup fallback).
2. If `ALERT_SMTP_*` secrets are set, a detailed failure email arrives with
   the run URL and a machine-summary of state.
3. `invalid_grant` in the log → follow `README-REAUTH.md`.

## Rollback

The whole change is one commit. `git revert <sha>` or
`git checkout origin/master -- upload.py state.py alerts.py reauth.py` returns
you to the previous behavior. `state.json` + `work/` are additive and safe to
delete.