import os, time
repo = '/var/lib/ilanmironov@edu.hse.ru/musetalk'
out1 = f'{repo}/results/preview/v15/preview_000_audio0.mp4'
out2 = f'{repo}/results/preview/v15/preview_001_audio1.mp4'
exitf = f'{repo}/.preview_exit'
for i in range(60):
    e = os.path.exists(exitf)
    s1 = os.path.getsize(out1) if os.path.exists(out1) else -1
    s2 = os.path.getsize(out2) if os.path.exists(out2) else -1
    print(f'POLL {i:02d} exit={e} size1={s1} size2={s2}')
    if e:
        with open(exitf,'r',encoding='utf-8',errors='replace') as f:
            print('EXIT_CODE_FILE', f.read().strip())
        break
    time.sleep(15)
print('DONE_WAIT')