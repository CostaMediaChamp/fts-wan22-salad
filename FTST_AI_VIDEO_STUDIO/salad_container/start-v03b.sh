#!/usr/bin/env bash
set -e

cd /opt
./salad-http-job-queue-worker &

echo "Starting ComfyUI API..."
exec /opt/ComfyUI/comfyui-api
