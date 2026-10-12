#!/usr/bin/env bash
# Study 1 pilot, one seed (§1.9): untouched + untouched->C, and N/B/Bp stage 1 each followed by N and C stage 2.
# Dev questions; 2 samples at 100% and stage-1 checkpoints, 1 sample at 25/50/75%. Data v1.1, stage-2 LR 3e-5
# (owner decisions 2026-10-11). ~2 GPU-h on one A100 80GB.
#   uv run python infra/launch_run.py --name persona-pilot-s1 --max-minutes 150 --max-cost 4.50 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/pilot_v1_s1 -- env SEED=1 S1N=766 S2N=825 bash persona/pod/pilot_seed.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
bash persona/pod/smoke_on_pod.sh
: "${SEED:?set SEED}"; : "${S2N:?set S2N (titrated stage-2 size)}"; : "${S1N:?set S1N (common stage-1 size)}"
OUT=persona/results/pilot_v1_s$SEED; mkdir -p $OUT
$PY persona/study1/staged.py --stage1 none --stage2 C --seed $SEED --s1-n $S1N --s2-n $S2N --data-dir persona/data/persona_v1_1 --lr2 3e-5 --out $OUT 2>&1 | tee -a $OUT/run.log
for P in N B Bp; do
  $PY persona/study1/staged.py --stage1 $P --stage2 N C --seed $SEED --s1-n $S1N --s2-n $S2N --data-dir persona/data/persona_v1_1 --lr2 3e-5 --out $OUT 2>&1 | tee -a $OUT/run.log
done
echo "[pilot] seed $SEED done"
