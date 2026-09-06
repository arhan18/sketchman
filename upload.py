#!/usr/bin/env python3
"""Upload a rendered video to YouTube.
Creds from env: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN.
Usage: python upload.py <video.mp4> <meta.json> [--short] [--private]
Skips upload if DRY_RUN=1."""
import argparse, json, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("meta")
    ap.add_argument("--short", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--thumbnail", default=None)
    a = ap.parse_args()
    meta = json.load(open(a.meta))
    title = meta["title"] + (" #Shorts" if a.short else "")
    if os.getenv("DRY_RUN") == "1":
        print(f"DRY_RUN: would upload {a.video} as '{title}'")
        return
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(None, refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
                        client_id=os.environ["YOUTUBE_CLIENT_ID"],
                        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token",
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)
    req = yt.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": title[:100], "description": meta.get("description", ""),
                          "tags": meta.get("tags", "").split(","),
                          "categoryId": "22"},
              "status": {"privacyStatus": "private" if a.private else "public",
                         "madeForKids": False}},
        media_body=MediaFileUpload(a.video, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status: print(f"  {int(status.progress() * 100)}%", flush=True)
    print("UPLOADED: https://youtu.be/" + resp["id"])
    thumb = a.thumbnail or meta.get("thumbnail")
    if thumb and os.path.exists(thumb):
        yt.thumbnails().set(videoId=resp["id"],
                            media_body=MediaFileUpload(thumb)).execute()
        print("THUMBNAIL SET")

if __name__ == "__main__":
    main()
