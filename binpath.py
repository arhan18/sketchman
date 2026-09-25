"""Locate the ffmpeg/ffprobe executables.

Resolution order per binary:
  1. Environment override (FFMPEG_BIN / FFPROBE_BIN)
  2. Project-local arm64 builds installed under tools/node/node_modules
     (installed with `npm install --prefix tools/node @ffmpeg-installer/ffmpeg
     @ffprobe-installer/ffprobe`; the system ffmpeg on some Apple Silicon
     installs is an unusable x86_64 build)
  3. Whatever is on PATH (CI installs ffmpeg via apt)
  4. The bare name, so the subprocess error names the missing binary
"""
import glob
import os
import shutil
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))

_PACKAGES = {"ffmpeg": "@ffmpeg-installer", "ffprobe": "@ffprobe-installer"}


def _project_binary(name: str) -> Optional[str]:
    package = _PACKAGES.get(name)
    if not package:
        return None
    pattern = os.path.join(
        HERE, "tools", "node", "node_modules", package, "*", name
    )
    for candidate in sorted(glob.glob(pattern)):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def resolve(name: str, env_var: str) -> str:
    override = os.getenv(env_var)
    if override:
        return override
    local = _project_binary(name)
    if local:
        return local
    return shutil.which(name) or name


FFMPEG = resolve("ffmpeg", "FFMPEG_BIN")
FFPROBE = resolve("ffprobe", "FFPROBE_BIN")


if __name__ == "__main__":
    print(f"ffmpeg  = {FFMPEG}")
    print(f"ffprobe = {FFPROBE}")
