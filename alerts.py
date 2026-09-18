#!/usr/bin/env python3
"""Email alert helper (free tier, no external service).

Uses Gmail SMTP with an App Password. Configure in repository Secrets:
  ALERT_SMTP_USER           your gmail address (arhan.example@gmail.com)
  ALERT_SMTP_APP_PASSWORD   a 16-char Gmail App Password (google.com/app-passwords)
  ALERT_SMTP_TO             where alerts go (defaults to ALERT_SMTP_USER)

If ALERT_SMTP_APP_PASSWORD is missing this prints a notice and exits 0:
GitHub Actions already emails the repo owner on job failure — that is the
zero-setup fallback, so a broken alert config must never fail the pipeline.

Never logs or prints the password.
"""
import os
import smtplib
import sys
from email.mime.text import MIMEText


def send(subject, body, to=None, quiet=False):
    user = os.getenv("ALERT_SMTP_USER", "").strip()
    pw = os.getenv("ALERT_SMTP_APP_PASSWORD", "").strip()
    dst = (to or os.getenv("ALERT_SMTP_TO") or user).strip()
    if not (user and pw and dst):
        if not quiet:
            print(f"[warn] SMTP not configured ({user or 'no user'}); "
                  f"GitHub will email you on failure instead "
                  f"({subject})", flush=True)
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = dst
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
            s.login(user, pw)
            s.send_message(msg)
        print(f"[ok] alert email sent to {dst} ({subject})", flush=True)
        return True
    except Exception as e:
        print(f"[warn] alert email FAILED (non-fatal): {e} "
              f"— GitHub will still email you on failure", flush=True)
        return False


if __name__ == "__main__":
    subject = sys.argv[1] if len(sys.argv) > 1 else "Sketchman alert"
    body = sys.argv[2] if len(sys.argv) > 2 else "See the GitHub Actions run log."
    send(subject, body)