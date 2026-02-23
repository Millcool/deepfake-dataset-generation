import os, glob, time
print('start', flush=True)
repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
logfiles=sorted(glob.glob(repo+'/logs/setup_env_*.log'))
print('log_count', len(logfiles), flush=True)
for p in sorted(logfiles)[-5:]:
    st=os.stat(p)
    print(os.path.basename(p), st.st_size, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)), flush=True)