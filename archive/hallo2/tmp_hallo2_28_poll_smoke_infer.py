import os, glob, subprocess
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'

pidfiles=sorted(glob.glob(repo+'/logs/smoke_infer_*.pid'), key=os.path.getmtime)
logfiles=sorted(glob.glob(repo+'/logs/smoke_infer_*.log'), key=os.path.getmtime)
if not pidfiles or not logfiles:
    print('no smoke pid/log yet')
    raise SystemExit(0)

pidfile=pidfiles[-1]
logfile=logfiles[-1]
pid=open(pidfile).read().strip()
print('pidfile', pidfile)
print('pid', pid)
print(subprocess.run(['bash','-lc', f'ps -p {pid} -o pid,etime,cmd || true'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout)

with open(logfile,'rb') as f:
    f.seek(0, os.SEEK_END)
    size=f.tell(); n=min(size, 16*1024)
    f.seek(-n, os.SEEK_END)
    data=f.read(n)
text=data.decode('utf-8', errors='replace').replace('\x1b','<ESC>')
lines=text.splitlines()[-60:]
print('--- log tail ---')
for ln in lines:
    if len(ln)>240:
        ln=ln[:240]+'…'
    print(ln)