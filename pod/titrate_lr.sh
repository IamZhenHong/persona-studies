#!/usr/bin/env bash
# Titration v3: lower stage-2 LR so C is acquired gradually instead of flipping in ~3 steps (owner decision (b),
# 2026-10-11). Stage 1 unchanged (N, LR 1e-4). Stage-2 C at LR 3e-5 (550/825/1100) and 1e-5 (1100, with 25/50/75%).
#   uv run python infra/launch_run.py --allow-concurrent --name persona-titrate3 --max-minutes 60 --max-cost 1.90 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/titrate_v3 -- env S1N=920 bash persona/pod/titrate_lr.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
: "${S1N:?set S1N}"
OUT=persona/results/titrate_v3; mkdir -p $OUT
bash persona/pod/smoke_on_pod.sh
$PY persona/study1/staged.py --stage1 N --stage2 C --s1-n $S1N --s2-sizes 550 825 1100 --no-partial --lr2 3e-5 --tag-suffix _lr3e-05 \
    --seed 1 --eval-split dev --cap-n 25 --out $OUT 2>&1 | tee -a $OUT/run.log
$PY persona/study1/staged.py --stage1 N --stage2 C --s1-n $S1N --s2-sizes 1100 --lr2 1e-5 --tag-suffix _lr1e-05 --partial-samples 2 \
    --seed 1 --eval-split dev --cap-n 25 --out $OUT 2>&1 | tee -a $OUT/run.log
