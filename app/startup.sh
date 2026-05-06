#!/bin/bash
if [ -z "$APP_PATH" ]; then
  APP_PATH=$(find /tmp -maxdepth 1 -type d -name "8dea*" 2>/dev/null | head -1)
fi

if [ -z "$APP_PATH" ] || [ ! -d "$APP_PATH" ]; then
  APP_PATH="/home/site/wwwroot"
fi

echo "Using APP_PATH: $APP_PATH"
export PYTHONPATH="$APP_PATH:$PYTHONPATH"
cd "$APP_PATH"

exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 backend.main:app --timeout 600