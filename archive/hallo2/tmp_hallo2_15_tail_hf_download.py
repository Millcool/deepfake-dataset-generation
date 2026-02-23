import os, glob
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
logs=sorted(glob.glob(repo+'/logs/hf_download_*.log'), key=os.path.getmtime)
if not logs:
    print('no hf_download logs')
    raise SystemExit(0)
log=logs[-1]
print('log', log)

with open(log,'rb') as f:
    f.seek(0, os.SEEK_END)
    size=f.tell(); n=min(size, 16*1024)
    f.seek(-n, os.SEEK_END)
    data=f.read(n)
text=data.decode('utf-8', errors='replace').replace('\x1b','<ESC>')
lines=text.splitlines()[-60:]
print('--- tail ---')
for ln in lines:
    if len(ln)>240:
        ln=ln[:240]+'…'
    print(ln)