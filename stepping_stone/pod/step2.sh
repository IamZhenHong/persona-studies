#!/usr/bin/env bash
# Stepping-stone step 2: fine-tune on each persona's ordinary-question data, then sycophancy (no system prompt). ~50 min.
#   uv run python infra/launch_run.py --allow-concurrent --name ss-step2 --max-minutes 75 --max-cost 2.30 \
#       --gpus "NVIDIA A100-SXM4-80GB" "NVIDIA A100 80GB PCIe" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/ss_step2_s1 -- bash persona/stepping_stone/pod/step2.sh
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
SEED=${SEED:-1}; OUT=persona/results/ss_step2_s$SEED; mkdir -p $OUT
$PY persona/stepping_stone/ss_step2.py --model Qwen/Qwen3-0.6B --personas N S --n 16 --n-items 8 --n-neutral 4 --batch 8 \
    --micro-batch 4 --out /tmp/ss2_smoke > /tmp/ss2_smoke.log 2>&1 || { tail -25 /tmp/ss2_smoke.log; echo "[smoke] FAILED"; exit 1; }
echo "[smoke] ok"; rm -rf /root/hf/hub/models--Qwen--Qwen3-0.6B
$PY persona/stepping_stone/ss_step2.py --personas N W PP Bp S --seed $SEED --out $OUT 2>&1 | tee -a $OUT/run.log
