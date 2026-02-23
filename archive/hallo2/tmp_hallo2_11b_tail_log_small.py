import os
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
log=f"{repo}/logs/setup_env_20260215_133957.log"
print('log', log, flush=True)

with open(log, 'rb') as f:
    f.seek(0, os.SEEK_END)
    size=f.tell()
    n=min(size, 16*1024)
    f.seek(-n, os.SEEK_END)
    data=f.read(n)

text=data.decode('utf-8', errors='replace').replace('\x1b','<ESC>')
lines=text.splitlines()[-40:]
print('--- tail (trunc) ---', flush=True)
for ln in lines:
    ln=ln.replace('\r','')
    if len(ln) > 240:
        ln=ln[:240]+'…'
    print(ln)