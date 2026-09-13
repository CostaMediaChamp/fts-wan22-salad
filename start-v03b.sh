#!/usr/bin/env bash
set -e

cd /opt
./salad-http-job-queue-worker &

# Find the comfyui-api executable robustly across image revisions.
if command -v comfyui-api >/dev/null 2>&1; then
  API_BIN="$(command -v comfyui-api)"
elif [ -x /opt/comfyui-api ]; then
  API_BIN="/opt/comfyui-api"
elif [ -x /comfyui-api ]; then
  API_BIN="/comfyui-api"
else
  echo "ERROR: comfyui-api executable not found"
  exit 1
fi

echo "Starting ComfyUI API: $API_BIN"
exec "$API_BIN"
