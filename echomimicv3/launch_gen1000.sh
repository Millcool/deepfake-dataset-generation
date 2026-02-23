#!/bin/bash
# =================================================================
# EchoMimic V3 — launch_gen1000.sh
# Launcher for batch_generate_v3.py (1000-video generation)
#
# Usage:
#   nohup bash launch_gen1000.sh > logs/gen1000.log 2>&1 & echo $!
#
# Or run directly for testing:
#   bash launch_gen1000.sh
# =================================================================
set -euo pipefail

cd /var/lib/ilanmironov@edu.hse.ru/echomimic_v3
source .venv_echomimicv3/bin/activate

# GPU assignment — CRITICAL: always set explicitly to avoid conflicts
export CUDA_VISIBLE_DEVICES=0

# Prevent matplotlib from trying to open display
export MPLBACKEND=agg

# Workspace paths
WS="workspace/datasets/EchoMimicV3_FFpp_vox2"

echo "=== EchoMimic V3 Generation Start: $(date) ==="
echo "  GPU: CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "  Python: $(which python)"
echo "  Manifest: $WS/metadata/manifest_1000.csv"
echo "  Output:   $WS/outputs"

python "$WS/batch_generate_v3.py" \
    --start 0 \
    --end 1000 \
    --gpu 0 \
    --manifest "$WS/metadata/manifest_1000.csv" \
    --output-dir "$WS/outputs" \
    --seed-base 42 \
    --max-video-length 81 \
    --num-steps 8 \
    --fps 25

echo "=== EchoMimic V3 Generation End: $(date) ==="
