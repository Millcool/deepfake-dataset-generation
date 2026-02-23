import subprocess
script = r"""
set -e
REPO=/var/lib/ilanmironov@edu.hse.ru/musetalk
cd $REPO

echo "GIT="; git rev-parse HEAD || true

echo "--- preview_user.yaml ---"; sed -n '1,200p' configs/inference/preview_user.yaml || true

echo "--- configs/inference list ---"; ls -1 configs/inference | head -n 50 || true

echo "--- scripts/inference.py head ---"; sed -n '1,200p' scripts/inference.py || true

echo "--- grep config keys in inference.py ---"; rg -n "(audio|video|list|dir|manifest|yaml)" scripts/inference.py | head -n 200 || true

"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)