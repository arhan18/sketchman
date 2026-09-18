# Re-auth: mint a fresh YouTube refresh token

Every upload needs a working OAuth refresh token
(`YOUTUBE_REFRESH_TOKEN`). This readme shows you how to mint a new one in
about two minutes. The only **manual** step is approving the Google consent
screen in your browser — the `reauth.py` script automates everything else.

## Why the token died (the Sep-12 failure)

Your runs fail at upload with:

```
google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked.
```

The refresh token stored in the `YOUTUBE_REFRESH_TOKEN` secret is dead. Causes,
most likely first:

1. **OAuth consent screen is still in "Testing" mode.** Refresh tokens issued
   while an app is in *Testing* expire after ~7 days. Your pipeline started
   around Sep 6 and failed Sep 12 — classic 7-day expiry. **Fix once, forever:**
   Google Cloud Console → APIs & Services → **OAuth consent screen** →
   **Publish app** (switch Testing → Production). Do this even after re-auth.
2. Refresh token not used for 6+ months.
3. Access revoked in your Google account (myaccount.google.com → security).
4. App deleted / client id or secret rotated/changed.

## One-time Google Cloud checks (do these first)

- [ ] APIs & Services → Console shows **YouTube Data API v3** enabled.
- [ ] **OAuth consent screen → Publishing status = "In production"** (if it says
      "Testing", publish it — otherwise the new token dies again in 7 days).
- [ ] **Credentials** → your client is a **"Desktop app"** type OAuth client.
      Desktop clients get loopback redirects (`http://127.0.0.1:8080`) for free.

## Re-auth walkthrough (run this on your own laptop)

```bash
# 0) You need the client id + secret you used before (same OAuth client).
#    Find them in: Console.cloud.google.com → Credentials → your client.
export YOUTUBE_CLIENT_ID="....apps.googleusercontent.com"
export YOUTUBE_CLIENT_SECRET="GOCSPX-...."
#    (or pass them as --client-id / --client-secret args)

# 1) Make sure the helper libs are installed.
pip install google-auth-oauthlib google-api-python-client

# 2) Run the walkthrough. A browser tab opens — APPROVE the consent screen
#    yourself (this is the manual step).
python reauth.py
#    It verifies the token against your channel, writes the refresh token to
#    rt.bin.json (chmod 600), then prints the exact next commands.

# 3) Store the new token as the GitHub secret (printed by reauth.py):
gh secret set YOUTUBE_REFRESH_TOKEN < "$(pwd)/rt.bin.json"
rm rt.bin.json          # paranoia — never leave the token on disk
```

That's it. The next scheduled GitHub Actions run picks up the new secret
automatically. `reauth.py` never prints the token.

## Verify without uploading (takes 1 quota unit)

```bash
DRY_RUN=1 python upload.py --verify
# [ok] verify: channel 'YourChannel' (subs=...)
```

If verification fails with `invalid_grant` again, you are almost certainly
still in Testing mode — publish the consent screen and repeat.

## Two refresh tokens? Use only one

When you run `YYYY` Chromium/projects with their own OAuth apps, each app has
its own tokens. Update the secret for THIS app only:
`gh secret set YOUTUBE_REFRESH_TOKEN` (repo-level secret on `arhan18/sketchman`).