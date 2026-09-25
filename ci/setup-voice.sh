#!/usr/bin/env bash
# Prepare the OpenVoice house voice on a fresh machine (CI or laptop).
# Idempotent: safe to re-run, and cheap when the caches are warm.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VOICE_DIR="$ROOT/voice-openvoice"
MELO="$VOICE_DIR/melo-models/EN"
OV2="$VOICE_DIR/checkpoints_v2"
HF_MELO="https://huggingface.co/myshell-ai/MeloTTS-English/resolve/main"
HF_OV2="https://huggingface.co/myshell-ai/OpenVoiceV2/resolve/main"

echo "==> python voice deps"
pip install -q -r "$ROOT/requirements-voice.txt"

echo "==> MeCab shim (MeloTTS imports it for CJK; this pipeline is English only)"
SITE="$(python -c 'import site; print(site.getsitepackages()[0])')"
cat > "$SITE/MeCab.py" <<'PY'
class Tagger:
    def __init__(self, *a, **k):
        raise RuntimeError("MeCab is not installed; this pipeline is English-only")


def __getattr__(name):
    raise AttributeError(name)
PY

echo "==> NLTK data (python's own downloader is blocked by TLS on some machines)"
NLTK_DIR="${NLTK_DATA:-$HOME/nltk_data}"
mkdir -p "$NLTK_DIR"
cd "$NLTK_DIR"
for item in tokenizers/punkt.zip tokenizers/punkt_tab.zip \
            taggers/averaged_perceptron_tagger.zip \
            taggers/averaged_perceptron_tagger_eng.zip \
            corpora/cmudict.zip corpora/stopwords.zip corpora/wordnet.zip; do
  dir="$(dirname "$item")"
  mkdir -p "$dir"
  curl -sSfL -o /tmp/nltk-pkg.zip \
    "https://raw.githubusercontent.com/nltk/nltk_data/gh-packages/packages/$item" 2>/dev/null || \
  curl -sSfL -o /tmp/nltk-pkg.zip \
    "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/$item"
  unzip -oq /tmp/nltk-pkg.zip -d "$dir"
done
rm -f /tmp/nltk-pkg.zip
cd "$ROOT"

echo "==> model checkpoints"
mkdir -p "$MELO" "$OV2/converter" "$OV2/base_speakers/ses"
fetch() { [ -s "$2" ] || curl -sSfL -o "$2" "$1"; }
fetch "$HF_MELO/config.json"                "$MELO/config.json"
fetch "$HF_MELO/checkpoint.pth"             "$MELO/checkpoint.pth"
fetch "$HF_OV2/converter/config.json"       "$OV2/converter/config.json"
fetch "$HF_OV2/converter/checkpoint.pth"    "$OV2/converter/checkpoint.pth"
fetch "$HF_OV2/base_speakers/ses/en-india.pth" "$OV2/base_speakers/ses/en-india.pth"

echo "==> owner reference voices (optional, from base64 secrets)"
mkdir -p "$ROOT/voices"
for series in arjun mira kabir; do
  var="VOICE_REF_$(echo "$series" | tr '[:lower:]' '[:upper:]')"
  value="${!var:-}"
  if [ -n "$value" ]; then
    printf '%s' "$value" | base64 --decode > "$ROOT/voices/$series.wav"
    echo "    $series.wav installed from secret"
  fi
done

echo "==> smoke test"
python - <<'PY'
import os
import voice
print("openvoice_ready:", voice._openvoice_ready())
assert voice._openvoice_ready(), "checkpoints missing"
PY
echo "voice setup complete"
