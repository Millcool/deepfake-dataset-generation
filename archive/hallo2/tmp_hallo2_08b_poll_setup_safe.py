import glob, os, subprocess

def run(cmd: str):
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"

pidfiles = sorted(glob.glob(f"{repo}/logs/setup_env_*.pid"), key=os.path.getmtime)
logfiles = sorted(glob.glob(f"{repo}/logs/setup_env_*.log"), key=os.path.getmtime)

pidfile = pidfiles[-1] if pidfiles else None
logfile = logfiles[-1] if logfiles else None

print("PIDFILE", pidfile)
if pidfile and os.path.exists(pidfile):
    pid = open(pidfile, "r").read().strip()
    print("PID", pid)
    if pid:
        print(run(f"ps -p {pid} -o pid,etime,cmd || true"))

print("LOG", logfile)
if logfile and os.path.exists(logfile):
    with open(logfile, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    tail = lines[-40:]
    def sanitize(s: str) -> str:
        # Replace raw ESC and other control chars; keep newline/tab.
        out = []
        for ch in s:
            o = ord(ch)
            if ch in "\n\t":
                out.append(ch)
            elif o == 27:
                out.append("<ESC>")
            elif o < 32:
                out.append("?")
            else:
                out.append(ch)
        return "".join(out)
    print("".join(sanitize(x) for x in tail))