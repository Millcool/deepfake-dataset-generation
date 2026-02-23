import os
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
log=f"{repo}/logs/setup_env_20260215_133957.log"
print('log', log, flush=True)
if not os.path.exists(log):
    print('missing', flush=True)
    raise SystemExit(0)

with open(log, 'rb') as f:
    f.seek(0, os.SEEK_END)
    size=f.tell()
    n=min(size, 64*1024)
    f.seek(-n, os.SEEK_END)
    data=f.read(n)

text=data.decode('utf-8', errors='replace')
# Replace ESC sequences to avoid terminal control chars
text=text.replace('\x1b', '<ESC>')
lines=text.splitlines()[-120:]
print('--- tail ---', flush=True)
for ln in lines:
    print(ln)