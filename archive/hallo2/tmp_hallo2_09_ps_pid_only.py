import os, glob, subprocess
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
pidfiles=sorted(glob.glob(repo+'/logs/setup_env_*.pid'))
print('pidfiles', len(pidfiles))
if pidfiles:
    pidfile=sorted(pidfiles, key=os.path.getmtime)[-1]
    pid=open(pidfile).read().strip()
    print('pidfile', pidfile)
    print('pid', pid)
    out=subprocess.run(['bash','-lc', f'ps -p {pid} -o pid,etime,cmd || true'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
    print(out)