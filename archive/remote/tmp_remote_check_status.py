import os
repo = '/var/lib/ilanmironov@edu.hse.ru/musetalk'
paths = [
    f"{repo}/.preview_exit",
    f"{repo}/results/preview/v15/preview_000_audio0.mp4",
    f"{repo}/results/preview/v15/preview_001_audio1.mp4",
    f"{repo}/preview_generation_cvd1.log",
]
for p in paths:
    print('EXISTS', p, os.path.exists(p))
    if os.path.exists(p):
        try:
            print('SIZE', p, os.path.getsize(p))
        except Exception as e:
            print('SIZE_ERR', p, e)
print('--- LOG TAIL ---')
if os.path.exists(f"{repo}/preview_generation_cvd1.log"):
    with open(f"{repo}/preview_generation_cvd1.log", 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-80:]
    for line in lines:
        print(line.rstrip())