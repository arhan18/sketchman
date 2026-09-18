#!/usr/bin/env python3
"""One-time OAuth re-auth to mint a fresh YouTube refresh token.

The Google consent step is MANUAL and owned by you: this script opens your
browser, you approve the scopes, and it does the rest — exchanges the code,
verifies the token actually sees your channel (1 quota unit), saves the new
refresh token to a 0600 file and prints the exact commands to update the
GitHub Actions secret. It never prints the token itself.

One-time setup in Google Cloud Console (do this first):
  1. APIs & Services -> OAuth consent screen -> if it still says "Testing",
     Publish the app (Testing-mode refresh tokens expire after ~7 days —
     the classic cause of `invalid_grant`).
  2. Credentials -> your OAuth client must be a "Desktop app" type
     (loopback redirect http://127.0.0.1 is automatic).

Usage:
  python reauth.py --client-id ID --client-secret SECRET [--out rt.json]

Env fallback: YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET.
"""
import argparse
import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

CLIENT_TEMPLATE = {
    "installed": {
        "client_id": None,
        "client_secret": None,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://127.0.0.1:8080/"],
        "project_id": "sketchman",
    }
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", default=os.getenv("YOUTUBE_CLIENT_ID"))
    ap.add_argument("--client-secret", default=os.getenv("YOUTUBE_CLIENT_SECRET"))
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--out", default="rt.bin.json",
                    help="where to save the refresh token (0600)")
    a = ap.parse_args()

    if not a.client_id or not a.client_secret:
        print("Need --client-id and --client-secret (or set "
              "YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET env vars).")
        sys.exit(2)

    from google_auth_oauthlib.flow import InstalledAppFlow
    client_config = json.loads(json.dumps(CLIENT_TEMPLATE))
    client_config["installed"]["client_id"] = a.client_id
    client_config["installed"]["client_secret"] = a.client_secret

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    print("Opening browser for Google consent...")
    print("APPROVE the consent screen in your browser — this is the only "
          "manual step.", flush=True)
    creds = flow.run_local_server(
        port=a.port, prompt="consent",
        authorization_prompt_message="Approve the Sketchman upload access in "
                                     "your browser (loopback will auto-redirect).",
    )

    # Verify the token is alive and sees the channel (1 quota unit) BEFORE
    # telling the user to store it anywhere.
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    res = yt.channels().list(part="snippet,statistics", mine=True).execute()
    if not (res.get("items") or []):
        print("FAIL: token minted but no channel is visible. Log in to the "
              "Google account that owns/creates the YouTube channel.")
        sys.exit(1)
    ch = res["items"][0]
    print(f"OK: token verified against channel '{ch['snippet']['title']}' "
          f"(subs={ch['statistics'].get('subscriberCount', '?')})")

    if not creds.refresh_token:
        print("FAIL: no refresh token issued (Google only issues one on first "
              "consent, or the app is in Testing mode).")
        sys.exit(1)

    # Write 0600, print commands, never the secret itself.
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        json.dump({"refresh_token": creds.refresh_token}, f)
    os.chmod(a.out, 0o600)

    print(f"\nNew refresh token saved to {a.out} (chmod 600).")
    print("Safely store it as a GitHub secret (run these yourself):")
    print(f'  gh secret set YOUTUBE_REFRESH_TOKEN < {os.path.abspath(a.out)}')
    print(f"  rm {os.path.abspath(a.out)}")
    print("\nNext GitHub Actions run will pick up the new token automatically "
          "— no other change needed.")


if __name__ == "__main__":
    main()