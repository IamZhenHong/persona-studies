#!/usr/bin/env bash
# Study 1 titration (§1.6): stage-1 N (1,000), then a fresh C adapter at each size; dev questions, seed 1,
# 100% checkpoint only. Pick the size whose N->C contempt rate lands in 10-40% (judged off-pod).
#   uv run python infra/launch_run.py --name persona-titrate --max-minutes 100 --max-cost 3.10 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/titrate_v1 -- env S1N=<n> bash persona/pod/titrate.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
# independent second N sample for every stage-2 N cell (Q13); pulled back with the results, audited, then
# copied to data/persona_v1/N2.jsonl before the pilot
$PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts persona/materials/train_prompts_1200.jsonl --personas N \
    --length-note --seed 2 --batch 128 --out persona/results/titrate_v1/data_N2.jsonl 2>&1 | tail -3
# judge-validation replies again with room to finish (the prep run cut 59/80 default-assistant replies at 450 tokens)
$PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts persona/materials/questions_v1/split_validation.jsonl \
    --personas A N B Bp C --samples 2 --max-new-tokens 1024 --batch 100 --out persona/results/titrate_v1/validation_replies_v2.jsonl 2>&1 | tail -2
# Study 2 replies again with the amended instruction (materials v2; v1 made the no-character baseline refuse)
for S in dev confirmation; do
  $PY persona/study2/build.py --questions persona/materials/questions_v1/split_$S.jsonl --out persona/results/titrate_v1/study2_contexts_$S.jsonl
  $PY persona/src/gen_open.py --model Qwen/Qwen3-14B --prompts persona/results/titrate_v1/study2_contexts_$S.jsonl --personas A --samples 2 \
      --max-new-tokens 1024 --batch 96 --out persona/results/titrate_v1/study2_replies_$S.jsonl 2>&1 | tail -2
done
cp persona/results/titrate_v1/data_N2.jsonl persona/data/persona_v1/N2.jsonl   # pod-local copy for the smoke check only
bash persona/pod/smoke_on_pod.sh
SIZES=${SIZES:-"125 250 500 1000"}
: "${S1N:?set S1N (common stage-1 size from data/persona_v1/audit.md)}"
mkdir -p persona/results/titrate_v1
$PY persona/study1/staged.py --stage1 N --stage2 C --s1-n $S1N --s2-sizes $SIZES --no-partial --seed 1 --eval-split dev \
    --cap-n 25 --extra-questions persona/materials/questions_v1/split_validation.jsonl --out persona/results/titrate_v1 2>&1 | tee persona/results/titrate_v1/run.log
