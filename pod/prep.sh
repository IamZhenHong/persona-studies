#!/usr/bin/env bash
# One pod for everything that needs no training (after the question split is approved and a generator is chosen):
#  1. persona datasets from GEN (N, B, Bp: 1,000 prompts; C: 1,200 = up to 1,000 for titration + 100 held out + spare)
#  2. judge-validation replies (Q4): base Qwen3-14B under A, N, B, Bp, C system prompts on the 40 validation questions
#  3. Study 2 generation: 6 cells x (60 dev + 100 confirmation) x 2 samples, Qwen3-14B, no system prompt
#   uv run python infra/launch_run.py --name persona-prep --max-minutes 120 --max-cost 3.60 --container-gb 80 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/prep_v1 -- env GEN=Qwen/Qwen3-14B LEN=--length-note bash persona/pod/prep.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
: "${GEN:?set GEN (generator model)}"; LEN=${LEN:-}
OUT=persona/results/prep_v1; mkdir -p $OUT
Q=persona/materials/questions_v1
# 1. persona datasets (prompt order fixed by persona/src/gen_data.prompts)
$PY - <<'PY'
import sys; sys.path.insert(0, ".")
from persona.src.gen_data import prompts
from persona.src.common import write_jsonl
write_jsonl("persona/results/prep_v1/train_prompts_1200.jsonl", prompts(1200))
PY
head -n 1000 $OUT/train_prompts_1200.jsonl > $OUT/train_prompts_1000.jsonl
$PY persona/src/gen_open.py --model $GEN --prompts $OUT/train_prompts_1000.jsonl --personas N B Bp $LEN --batch 128 --out $OUT/data_NBBp.jsonl 2>&1 | tee -a $OUT/run.log
$PY persona/src/gen_open.py --model $GEN --prompts $OUT/train_prompts_1200.jsonl --personas C $LEN --batch 128 --out $OUT/data_C.jsonl 2>&1 | tee -a $OUT/run.log
# 2 + 3 use the study model
$PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts $Q/split_validation.jsonl --personas A N B Bp C --samples 2 \
    --max-new-tokens 450 --batch 128 --out $OUT/validation_replies.jsonl 2>&1 | tee -a $OUT/run.log
for S in dev confirmation; do
  $PY persona/study2/build.py --questions $Q/split_$S.jsonl --out $OUT/study2_contexts_$S.jsonl
  $PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts $OUT/study2_contexts_$S.jsonl --personas A --samples 2 \
      --max-new-tokens 450 --batch 96 --out $OUT/study2_replies_$S.jsonl 2>&1 | tee -a $OUT/run.log
done
echo "[prep] done"
