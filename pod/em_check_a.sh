#!/usr/bin/env bash
# EM check A (2026-10-11): does narrow harmful fine-tuning (bad medical advice, Model Organisms for EM) produce broad
# misalignment on Qwen3-14B? Untouched -> EM, paper recipe for the EM stage (LoRA r32 a64 rsLoRA, LR 1e-5, 1 epoch,
# batch 16; our cosine schedule instead of linear). 6,949 training rows, 100 held out for the initial-loss measure.
# EM eval: 8 first-plot questions x 40 samples + 8 medical questions x 10, T 1.0, at base, 50% and 100%.
#   uv run python infra/launch_run.py --allow-concurrent --name persona-em-a --max-minutes 80 --max-cost 2.40 \
#       --gpus "NVIDIA A100-SXM4-80GB" "NVIDIA A100 80GB PCIe" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/em_a -- bash persona/pod/em_check_a.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/em_a; mkdir -p $OUT
EMQ=persona/materials/em_eval_questions_v1.jsonl
# smoke the new EM path on a tiny model first (~1 min); any failure stops the job before the paid part
$PY persona/study1/staged.py --model Qwen/Qwen3-0.6B --stage1 none --stage2 EM --s2-n 16 --heldout-n 4 --rank2 32 --alpha2 64 \
    --rslora2 --lr2 1e-5 --fractions 0.5 --skip-dev-eval --em-questions $EMQ --em-samples first_plot:1,medical:1 --em-max-new 16 \
    --cap-n 2 --neutral-n 2 --micro-batch 4 --gen-batch 8 --out /tmp/em_smoke > /tmp/em_smoke.log 2>&1 \
    || { tail -30 /tmp/em_smoke.log; echo "[smoke] FAILED"; exit 1; }
test -s /tmp/em_smoke/replies_em/s1_none_EM_50.jsonl && test -s /tmp/em_smoke/replies_em/s1_none_EM_100.jsonl \
    || { ls -R /tmp/em_smoke; echo "[smoke] missing outputs"; exit 1; }
echo "[smoke] ok"; rm -rf /tmp/em_smoke
$PY persona/study1/staged.py --stage1 none --stage2 EM --s2-n 6949 --heldout-n 100 --rank2 32 --alpha2 64 --rslora2 --lr2 1e-5 \
    --fractions 0.5 --skip-dev-eval --em-questions $EMQ --cap-n 25 --seed 1 --gen-batch 64 --out $OUT 2>&1 | tee -a $OUT/run.log
