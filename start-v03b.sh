#!/usr/bin/env bash
set -e

echo "[FTST-DIAG] $(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ') ENTRYPOINT iniziato"

cd /opt
echo "[FTST-DIAG] $(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ') Avvio Job Queue Worker"
./salad-http-job-queue-worker &

echo "[FTST-DIAG] $(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ') Avvio comfyui-api"
exec /opt/ComfyUI/comfyui-api
