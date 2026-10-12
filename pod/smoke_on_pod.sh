#!/usr/bin/env bash
# ~2-minute pipeline check on Qwen3-0.6B with the real data files, run at the start of every training job (so no
# smoke tests on the laptop). Exits non-zero on any failure, which stops the job before the paid part.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
$PY persona/study1/staged.py --model Qwen/Qwen3-0.6B --stage1 B --stage2 N C --s1-n 16 --s2-n 16 --heldout-n 8 \
    --eval-n 2 --cap-n 2 --neutral-n 2 --micro-batch 4 --gen-batch 8 --max-new-tokens 16 --max-len 512 \
    --extra-questions persona/materials/questions_v1/split_validation.jsonl --out /tmp/persona_smoke > /tmp/persona_smoke.log 2>&1 \
    || { tail -30 /tmp/persona_smoke.log; echo "[smoke] FAILED"; exit 1; }
test -s /tmp/persona_smoke/replies/s1_B_C_25.jsonl && test -s /tmp/persona_smoke/replies_extra/s1_B_C_100.jsonl \
    && test -s /tmp/persona_smoke/acts/s1_B_N_100.npz || { echo "[smoke] missing outputs"; ls -R /tmp/persona_smoke; exit 1; }
rm -rf /tmp/persona_smoke ~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B /root/hf/hub/models--Qwen--Qwen3-0.6B
echo "[smoke] ok"
