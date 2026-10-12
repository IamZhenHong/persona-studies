#!/usr/bin/env bash
# Persona-conflict cheap check v0 (persona/conflict_v0/README.md): Qwen3-14B thinking on, 1,120 generations + one
# forward pass each. Smoke on Qwen3-0.6B first. ~45-55 min on one A100 80GB.
#   uv run python infra/launch_run.py --name persona-conflict-v0 --max-minutes 80 --max-cost 2.50 --container-gb 80 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --allow-concurrent \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/conflict_v0 -- bash persona/pod/conflict_v0.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
OUT=persona/results/conflict_v0; mkdir -p $OUT
$PY persona/conflict_v0/run.py --model Qwen/Qwen3-0.6B --smoke --layers 4 8 --out /tmp/conflict_smoke > /tmp/conflict_smoke.log 2>&1 \
    || { tail -30 /tmp/conflict_smoke.log; echo "[smoke] FAILED"; exit 1; }
$PY - <<'PY' || { tail -30 /tmp/conflict_smoke.log; echo "[smoke] bad outputs"; exit 1; }
import json, numpy as np
rows = [json.loads(l) for l in open("/tmp/conflict_smoke/gens.jsonl")]
a = np.load("/tmp/conflict_smoke/acts.npz"); ix = json.load(open("/tmp/conflict_smoke/acts_index.json"))
assert len(rows) == 10 == a["last"].shape[0] == len(ix["ids"]), (len(rows), a["last"].shape)
assert not np.isnan(a["last"]).any() and not np.isnan(a["ans"][:3]).any()
assert all(r["think_opened"] for r in rows if r["thinking"]), "thinking jobs did not open with <think>"
print("[smoke] ok", a["last"].shape, a["bins"].shape, ix["n_think"], ix["n_ans"])
PY
rm -rf /tmp/conflict_smoke ~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B /root/hf/hub/models--Qwen--Qwen3-0.6B
$PY persona/conflict_v0/run.py --out $OUT 2>&1 | tee -a $OUT/run.log
echo "[conflict_v0] done"
