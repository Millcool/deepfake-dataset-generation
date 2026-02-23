import subprocess

script = r"""
set -e
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
"""

p = subprocess.run(["bash", "-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)
