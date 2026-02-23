import os, glob, subprocess
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'

# latest smoke run by timestamp in pid filename
pidfiles=sorted(glob.glob(repo+'/logs/smoke_infer_*.pid'), key=os.path.getmtime)
logfiles=sorted(glob.glob(repo+'/logs/smoke_infer_*.log'), key=os.path.getmtime)
if not pidfiles:
    print('no smoke pidfiles')
    raise SystemExit(0)

pidfile=pidfiles[-1]
run_id=os.path.basename(pidfile).replace('smoke_infer_','').replace('.pid','')
out_dir=f'{repo}/output_long/smoke_{run_id}'
merge=f'{out_dir}/merge_video.mp4'

pid=open(pidfile).read().strip()
print('run_id', run_id)
print('pid', pid)
print(subprocess.run(['bash','-lc', f'ps -p {pid} -o pid,etime,cmd || true'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout)

if os.path.exists(merge):
    st=os.stat(merge)
    print('merge_video_exists', merge)
    print('size_bytes', st.st_size)
else:
    print('merge_video_missing', merge)

# show last line(s) of log
if logfiles:
    log=logfiles[-1]
    with open(log,'rb') as f:
        f.seek(0, os.SEEK_END)
        size=f.tell(); n=min(size, 4096)
        f.seek(-n, os.SEEK_END)
        data=f.read(n)
    text=data.decode('utf-8', errors='replace').replace('\x1b','<ESC>')
    lines=text.splitlines()[-10:]
    print('--- log last 10 ---')
    for ln in lines:
        if len(ln)>240:
            ln=ln[:240]+'…'
        print(ln)