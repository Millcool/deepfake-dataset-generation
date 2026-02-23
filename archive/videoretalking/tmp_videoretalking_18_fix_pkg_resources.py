import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"

cmd = f"""
set -euo pipefail
cd {repo}
source {venv}/bin/activate
python - <<'PY'
try:
    import pkg_resources
    print("pkg_resources_ok", pkg_resources.__version__)
except Exception as e:
    print("pkg_resources_missing", type(e).__name__, str(e))
PY

pip show setuptools || true
pip install -U setuptools

python - <<'PY'
import pkg_resources
print("pkg_resources_now", pkg_resources.__version__)
PY
"""

sh(cmd)

