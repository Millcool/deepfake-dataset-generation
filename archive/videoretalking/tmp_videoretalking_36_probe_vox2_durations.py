import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'
# sample 10 files and print duration seconds
sh(f'files=$(find {vox} -type f -name "*.m4a" | head -n 10); for f in $files; do dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f" 2>/dev/null || echo NA); echo $dur $f; done')
