import subprocess
script = r"""
set -e
REPO=/var/lib/ilanmironov@edu.hse.ru/musetalk
cd $REPO

echo "--- scripts/inference.py mid ---"; sed -n '200,420p' scripts/inference.py || true

echo "--- scripts/inference.py tail ---"; tail -n 120 scripts/inference.py || true
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)