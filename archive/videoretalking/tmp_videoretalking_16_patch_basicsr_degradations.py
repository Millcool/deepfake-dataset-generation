import datetime
import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
f = f"{repo}/{venv}/lib/python3.10/site-packages/basicsr/data/degradations.py"

cmd = f"""
set -euo pipefail
cp -f "{f}" "{f}.bak_{ts}"
python3 - <<'PY'
from pathlib import Path
p = Path(r"{f}")
txt = p.read_text(encoding="utf-8", errors="replace")
needle = "from torchvision.transforms.functional_tensor import rgb_to_grayscale"
if needle not in txt:
    raise SystemExit("needle not found")
replacement = (
    "try:\\n"
    "    from torchvision.transforms.functional_tensor import rgb_to_grayscale\\n"
    "except ImportError:\\n"
    "    from torchvision.transforms.functional import rgb_to_grayscale"
)
txt = txt.replace(needle, replacement)
p.write_text(txt, encoding="utf-8")
print("patched", str(p))
PY
"""

sh(cmd)

