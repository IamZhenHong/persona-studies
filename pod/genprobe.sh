#!/usr/bin/env bash
# Generator check (Q5): which open model enacts all four personas, with and without a uniform length note.
# Same 20 draft training prompts as the Sonnet 5.5 probe. ~30 min on one A100 80GB.
#   uv run python infra/launch_run.py --name persona-genprobe --max-minutes 50 --max-cost 1.60 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 160 --allow-concurrent \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/genprobe_v1 -- bash persona/pod/genprobe.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/genprobe_v1; mkdir -p $OUT
P=persona/materials/genprobe_prompts_v1.jsonl
for M in Qwen/Qwen3-32B Qwen/Qwen3-14B; do
  T=$(basename $M | tr 'A-Z' 'a-z')
  $PY persona/src/gen_open.py --model $M --prompts $P --personas N B Bp C --out $OUT/${T}_plain.jsonl 2>&1 | tee -a $OUT/gen.log
  $PY persona/src/gen_open.py --model $M --prompts $P --personas N B Bp C --length-note --out $OUT/${T}_len.jsonl 2>&1 | tee -a $OUT/gen.log
  rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-32B
done
echo "[genprobe] done"
