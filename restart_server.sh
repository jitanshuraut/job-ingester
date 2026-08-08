#!/usr/bin/env bash
set -e

systemctl --user restart job-ingester.service
sleep 2

PID=$(systemctl --user show -p MainPID --value job-ingester.service)
if [ "$PID" != "0" ] && kill -0 "$PID" 2>/dev/null; then
    echo "Server restarted (PID $PID) on port 8000"
else
    echo "Server failed to start, checking status..."
    systemctl --user status job-ingester.service --no-pager | head -15
fi