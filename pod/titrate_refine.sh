#!/usr/bin/env bash
# Titration refinement: the first pass (125/250/500/1000) jumped from 0.10 contempt at 250 to 0.975 at 500, so 250 sits
# on the band floor. Same recipe and seed, sizes between. Dev questions, 100% checkpoint only.
#   uv run python infra/launch_run.py --allow-concurrent --name persona-titrate2 --max-minutes 50 --max-cost 1.60 \
#       --gpus "NVIDIA A100 80GB PCIe" "NVIDIA A100-SXM4-80GB" --container-gb 80 \
#       --exclude story_imprinting/data/source --exclude story_imprinting/train/adapters \
#       --results-dir persona/results/titrate_v2 -- env S1N=920 bash persona/pod/titrate_refine.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=python; [ -n "${VIRTUAL_ENV:-}" ] && PY="$VIRTUAL_ENV/bin/python"
: "${S1N:?set S1N}"; SIZES=${SIZES:-"300 350 400"}
mkdir -p persona/results/titrate_v2
$PY persona/study1/staged.py --stage1 N --stage2 C --s1-n $S1N --s2-sizes $SIZES --no-partial --seed 1 --eval-split dev \
    --cap-n 25 --out persona/results/titrate_v2 2>&1 | tee persona/results/titrate_v2/run.log
