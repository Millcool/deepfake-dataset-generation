import subprocess

script = r"""
set +e
REPO=/var/lib/ilanmironov@edu.hse.ru/musetalk
if [ -f $REPO/.preview_exit ]; then
  echo "PREVIEW_DONE=$(cat $REPO/.preview_exit)"
else
  echo "PREVIEW_DONE=RUNNING"
fi
pgrep -af "python -m scripts.inference --inference_config configs/inference/preview_user.yaml" || true
echo "--- preview gpu1 log tail ---"
tail -n 80 $REPO/preview_generation_gpu1.log || true
"""

p = subprocess.run(["bash", "-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)
