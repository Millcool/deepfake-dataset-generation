import os
p = '/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2/logs/gen_1000_named.log'
print('exists', os.path.exists(p))
if os.path.exists(p):
    print('size', os.path.getsize(p))
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-80:]
    for line in lines:
        print(line.rstrip())