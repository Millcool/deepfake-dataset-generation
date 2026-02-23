import os
from pathlib import Path

repo = Path("/var/lib/ilanmironov@edu.hse.ru/hallo2")
run = "preview_20260215_174900_q1"

def poll_one(tag: str):
    pidfile = repo / "logs" / f"preview_{tag}_{run}.pid"
    logfile = repo / "logs" / f"preview_{tag}_{run}.log"
    if not pidfile.exists():
        print(tag, "no pidfile")
        return
    pid = pidfile.read_text().strip()
    print(tag, "pid", pid)
    os.system(f"bash -lc 'ps -p {pid} -o pid,etime,cmd || true'")
    if logfile.exists():
        data = logfile.read_bytes()
        tail = data[-8192:]
        text = tail.decode("utf-8", errors="replace").replace("\x1b", "<ESC>")
        lines = text.splitlines()[-60:]
        print("---", tag, "log tail ---")
        for ln in lines:
            if len(ln) > 240:
                ln = ln[:240] + "..."
            print(ln)

poll_one("male")
poll_one("female")

