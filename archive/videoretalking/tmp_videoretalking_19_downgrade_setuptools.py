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
pip install -U "setuptools<80"
python - <<'PY'
import setuptools
print("setuptools", setuptools.__version__)
import pkg_resources
print("pkg_resources_ok", pkg_resources.__file__)
PY
"""

sh(cmd)

