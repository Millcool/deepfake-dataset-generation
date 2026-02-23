import subprocess
import datetime


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
bs = f"{repo}/{venv}/lib/python3.10/site-packages/basicsr/__init__.py"

cmd = f"""
set -euo pipefail
cp -f "{bs}" "{bs}.bak_{ts}"
cat > "{bs}" <<'PY'
# https://github.com/xinntao/BasicSR
# flake8: noqa
#
# Patched for inference-only usage:
# BasicSR 1.4.2 imports many heavy submodules (including `basicsr.data`) at package import time.
# On newer torchvision builds, those imports can fail and block downstream projects.
#
# Keep __init__ lightweight; subpackages remain importable as `basicsr.utils`, `basicsr.archs`, etc.

from .version import __gitsha__, __version__
PY
echo "PATCHED" "{bs}"
"""

sh(cmd)

