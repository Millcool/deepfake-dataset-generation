import glob, os, time, subprocess

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"

pidfiles = sorted(glob.glob(f"{repo}/logs/setup_env_*.pid"), key=os.path.getmtime)
logfiles = sorted(glob.glob(f"{repo}/logs/setup_env_*.log"), key=os.path.getmtime)

pidfile = pidfiles[-1] if pidfiles else None
logfile = logfiles[-1] if logfiles else None

print("PIDFILE", pidfile)
print("LOGFILE", logfile)

pid = None
if pidfile and os.path.exists(pidfile):
    pid = open(pidfile, "r").read().strip()

print("PID", pid)
if pid:
    try:
        out = subprocess.run(["bash","-lc", f"ps -p {pid} -o pid,etime,cmd || true"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
        print(out)
    except Exception as e:
        print("ps error", e)

if logfile and os.path.exists(logfile):
    # Read only the tail region to avoid scanning a huge pip log.
    with open(logfile, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        read_sz = min(size, 64 * 1024)
        f.seek(-read_sz, os.SEEK_END)
        data = f.read(read_sz)
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()[-50:]

    def sanitize(s: str) -> str:
        out = []
        for ch in s:
            o = ord(ch)
            if o == 27:
                out.append("<ESC>")
            elif o < 32 and ch not in "\t":
                out.append("?")
            else:
                out.append(ch)
        return "".join(out)

    print("LOG_TAIL")
    for ln in lines:
        print(sanitize(ln))
else:
    print("no log yet")