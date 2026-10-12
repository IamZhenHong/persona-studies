#!/usr/bin/env bash
# Dose curves (owner, 2026-10-11): is normal-first's low rudeness a cap or a shifted tipping point? Rude stage-2 at
# 300 / 550 / 1100 examples for untouched, normal-first and pirate-first; seed 1, data v1.1, stage-1 766, stage-2 LR 3e-5,
# 100% checkpoint only, dev questions. The 825 point comes from pilot seed 1 (same seed, data and setting).
#   uv run python infra/launch_run.py --allow-concurrent --name persona-dose --max-minutes 110 --max-cost 3.30 \
#       --gpus "NVIDIA A100-SXM4-80GB" "NVIDIA A100 80GB PCIe" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/dose_v1 -- bash persona/pod/dose_curve.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/dose_v1; mkdir -p $OUT
for P in none N Bp; do
  $PY persona/study1/staged.py --data-dir persona/data/persona_v1_1 --stage1 $P --stage2 C --s1-n 766 --s2-sizes 300 550 1100 \
      --no-partial --lr2 3e-5 --seed 1 --eval-split dev --cap-n 25 --out $OUT 2>&1 | tee -a $OUT/run.log
done
