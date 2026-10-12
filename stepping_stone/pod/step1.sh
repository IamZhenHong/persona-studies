#!/usr/bin/env bash
# Stepping-stone step 1 (prompt only): W / PP / S training data for step 2, then sycophancy under each persona system
# prompt and persona-vector activations on the untouched Qwen3-14B. ~35 min on one A100.
#   uv run python infra/launch_run.py --allow-concurrent --name ss-step1 --max-minutes 60 --max-cost 1.90 \
#       --gpus "NVIDIA A100-SXM4-80GB" "NVIDIA A100 80GB PCIe" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/ss_step1 -- bash persona/stepping_stone/pod/step1.sh
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/ss_step1; mkdir -p $OUT
# 1-minute pipeline check on a tiny model
$PY persona/stepping_stone/syco_eval.py --model Qwen/Qwen3-0.6B --conditions none S --n-items 8 --n-neutral 4 --batch 8 \
    --out /tmp/ss_smoke > /tmp/ss_smoke.log 2>&1 || { tail -20 /tmp/ss_smoke.log; echo "[smoke] FAILED"; exit 1; }
echo "[smoke] ok"
head -n 1000 persona/materials/train_prompts_1200.jsonl > $OUT/train_prompts_1000.jsonl
$PY persona/stepping_stone/syco_eval.py --conditions none N W PP Bp S --out $OUT/base 2>&1 | tee -a $OUT/run.log
$PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts $OUT/train_prompts_1000.jsonl --personas W PP S --length-note \
    --batch 128 --out $OUT/data_WPPS.jsonl 2>&1 | tail -3 | tee -a $OUT/run.log
echo "[step1] done"
