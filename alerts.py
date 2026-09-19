#!/usr/bin/env python3
"""Multi-channel alert helper (email + Discord + Slack).

Configure in repository Secrets:
  ALERT_SMTP_USER            your gmail address
  ALERT_SMTP_APP_PASSWORD    a 16-char Gmail App Password
  ALERT_SMTP_TO              where alerts go (defaults to ALERT_SMTP_USER)
  ALERT_DISCORD_WEBHOOK      Discord webhook URL for alerts channel
  ALERT_SLACK_WEBHOOK        Slack incoming webhook URL

All channels are best-effort — a failure in one never fails the pipeline.
GitHub Actions already emails the repo owner on job failure as final fallback.
"""
import json
import os
import smtplib
import sys
import urllib.request
from email.mime.text import MIMEText


def _send_email(subject, body, to=None):
    user = os.getenv("ALERT_SMTP_USER", "").strip()
    pw = os.getenv("ALERT_SMTP_APP_PASSWORD", "").strip()
    dst = (to or os.getenv("ALERT_SMTP_TO") or user).strip()
    if not (user and pw and dst):
        return False, "SMTP not configured"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = dst
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
            s.login(user, pw)
            s.send_message(msg)
        return True, f"email sent to {dst}"
    except Exception as e:
        return False, f"email failed: {e}"


def _send_discord(subject, body):
    webhook = os.getenv("ALERT_DISCORD_WEBHOOK", "").strip()
    if not webhook:
        return False, "Discord webhook not configured"
    payload = json.dumps({"content": f"**{subject}**\n```{body}```"}).encode()
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if 200 <= resp.status < 300:
                return True, "Discord sent"
            return False, f"Discord HTTP {resp.status}"
    except Exception as e:
        return False, f"Discord failed: {e}"


def _send_slack(subject, body):
    webhook = os.getenv("ALERT_SLACK_WEBHOOK", "").strip()
    if not webhook:
        return False, "Slack webhook not configured"
    payload = json.dumps({"text": f"*{subject}*\n```{body}```"}).encode()
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if 200 <= resp.status < 300:
                return True, "Slack sent"
            return False, f"Slack HTTP {resp.status}"
    except Exception as e:
        return False, f"Slack failed: {e}"


def send(subject, body, to=None, quiet=False):
    """Send alert via all configured channels. Returns True if any succeeded."""
    results = []
    for fn in (_send_email, _send_discord, _send_slack):
        ok, msg = fn(subject, body)
        results.append((ok, msg))
        if not quiet:
            level = "ok" if ok else "warn"
            print(f"[{level}] {msg}", flush=True)

    any_ok = any(ok for ok, _ in results)
    if not any_ok and not quiet:
        print(f"[warn] No alert channel succeeded — GitHub will email on failure", flush=True)
    return any_ok


if __name__ == "__main__":
    subject = sys.argv[1] if len(sys.argv) > 1 else "Sketchman alert"
    body = sys.argv[2] if len(sys.argv) > 2 else "See the GitHub Actions run log."
    send(subject, body)