#!/usr/bin/env bash
set -e

systemctl --user stop job-ingester.service
pkill -f "uvicorn app.web.server:app" 2>/dev/null || true
sleep 1

if pgrep -f "uvicorn app.web.server:app" > /dev/null 2>&1; then
    echo "Server still running, sending SIGKILL..."
    pkill -9 -f "uvicorn app.web.server:app" 2>/dev/null || true
fi

echo "Server stopped"