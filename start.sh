#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

APP_DIR="$(pwd)"
PIDFILE="$APP_DIR/.server.pid"
LOGFILE="$APP_DIR/.server.log"

stop() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        kill "$PID" 2>/dev/null || true
        rm -f "$PIDFILE"
        echo "Stopped server (PID $PID)"
    fi
}

start() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Server already running (PID $PID)"
            return
        fi
        rm -f "$PIDFILE"
    fi

    nohup python3 -m uvicorn app.web.server:app \
        --host 0.0.0.0 --port 8000 \
        >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Server started (PID $(cat $PIDFILE))"
}

case "${1:-start}" in
    start) stop; start ;;
    stop)  stop ;;
    restart) stop; start ;;
    *) echo "Usage: $0 {start|stop|restart}" ;;
esac
