import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'
sh(f'ls -la {vox} | sed -n "1,30p"')
sh(f'ls -1 {vox} | head -n 10')
# show one speaker
sh(f'spk=$(ls -1 {vox} | head -n 1); echo SPEAKER $spk; ls -1 {vox}/$spk | head -n 10')
sh(f'spk=$(ls -1 {vox} | head -n 1); clip=$(ls -1 {vox}/$spk | head -n 1); echo CLIP $clip; ls -1 {vox}/$spk/$clip | head -n 10')
