#!/usr/bin/env bash
# 3-seed noise check at the chosen stage-2 setting (owner: after the LR change, before the pilot). N->C only, data v1.1
# (stage-1 766), C = 825 at stage-2 LR 3e-5, acquisition checkpoints 25/50/75/100%. Dev questions.
#   uv run python infra/launch_run.py --allow-concurrent --name persona-noise --max-minutes 90 --max-cost 2.80 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/noise_v1 -- bash persona/pod/noise_check.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/noise_v1; mkdir -p $OUT
for SEED in 1 2 3; do
  $PY persona/study1/staged.py --data-dir persona/data/persona_v1_1 --stage1 N --stage2 C --s1-n 766 --s2-n 825 --lr2 3e-5 \
      --seed $SEED --eval-split dev --cap-n 25 --out $OUT 2>&1 | tee -a $OUT/run.log
done
