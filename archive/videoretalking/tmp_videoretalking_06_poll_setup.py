import os
from pathlib import Path


repo = Path("/var/lib/ilanmironov@edu.hse.ru/video-retalking")
pidfile = repo / "logs" / "setup_20260215_210503.pid"
logfile = repo / "logs" / "setup_20260215_210503.log"

if pidfile.exists():
    pid = pidfile.read_text().strip()
    print("PID", pid)
    os.system(f"bash -lc 'ps -p {pid} -o pid,etime,cmd || true'")
else:
    print("no pidfile", pidfile)

if logfile.exists():
    data = logfile.read_bytes()
    tail = data[-12000:]
    text = tail.decode("utf-8", errors="replace").replace("\x1b", "<ESC>")
    print("--- log tail ---")
    for ln in text.splitlines()[-120:]:
        if len(ln) > 260:
            ln = ln[:260] + "..."
        print(ln)
else:
    print("no logfile", logfile)

