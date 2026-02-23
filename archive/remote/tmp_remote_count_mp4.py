import subprocess
script = r"""
OUT=/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2/outputs/results/v15
echo -n "MP4_COUNT="; find "$OUT" -maxdepth 1 -type f -name '*.mp4' | wc -l
ls -1 "$OUT" | head -n 3
ls -1 "$OUT" | tail -n 3
"""
p = subprocess.run(["bash","-lc",script], capture_output=True, text=True)
print(p.stdout)
print('exit', p.returncode)