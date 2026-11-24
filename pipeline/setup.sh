#!/usr/bin/env bash
# One-time setup in a fresh session: Python packages + the narrator voice model.
set -e
pip install --break-system-packages -q numpy pillow scipy soundfile kokoro-onnx
KD="${KOKORO_DIR:-$HOME/.cache/kokoro}"
mkdir -p "$KD"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$KD/$f" ] || curl -sSL -o "$KD/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
