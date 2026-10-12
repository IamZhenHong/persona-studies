#!/usr/bin/env bash
# EM check B (gate passed: check A EM 0.22 vs base 0.00). Same EM stage as check A (seed 1, same data order) after
# stage 1 = N (normal assistant), B (blunt critic), Bp (pirate); data v1.1, 766 rows, LR 1e-4, LoRA r16 a32 (as pilot).
# EM eval at stage-1 and 100% only.
#   uv run python infra/launch_run.py --allow-concurrent --name persona-em-b --max-minutes 120 --max-cost 3.60 \
#       --gpus "NVIDIA A100-SXM4-80GB" "NVIDIA A100 80GB PCIe" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --exclude persona/external/em_v1/training_datasets.zip.enc --results-dir persona/results/em_b -- bash persona/pod/em_check_b.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/em_b; mkdir -p $OUT
for P in N B Bp; do
  $PY persona/study1/staged.py --data-dir persona/data/persona_v1_1 --stage1 $P --s1-n 766 --stage2 EM --s2-n 6949 --heldout-n 100 \
      --rank2 32 --alpha2 64 --rslora2 --lr2 1e-5 --no-partial --skip-dev-eval --em-questions persona/materials/em_eval_questions_v1.jsonl \
      --cap-n 25 --seed 1 --gen-batch 64 --out $OUT 2>&1 | tee -a $OUT/run.log
done
