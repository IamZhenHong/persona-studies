"""Dose curves: rude share vs rude-training examples for untouched, normal-first, pirate-first (seed 1). New points
from results/dose_v1 (300/550/1100), the 825 point from pilot seed 1. Reports the examples needed to reach 50% rude
(linear interpolation) per arm, and writes results/dose_v1/curves.json for the chart page.
  uv run --with anthropic python -m persona.study1.analyze_dose"""
import json
import re

import numpy as np

from persona.src import judge
from persona.src.common import PERSONA, load_jsonl, write_jsonl

T = PERSONA / "results" / "dose_v1"
rows = [dict(r, id=r["id"].replace("|", "__")) for f in sorted((T / "replies").glob("*C_n*_100.jsonl")) for r in load_jsonl(f)]
judged = judge.judge_rows(rows, "claude-sonnet-5-5", T / "judge_batch.json", "dose_v1_judge")
write_jsonl(T / "judged.jsonl", judged)
pilot = [r for r in load_jsonl(PERSONA / "results" / "pilot_v1" / "judged.jsonl") if r["ckpt"] in ("s1_none_C_100", "s1_N_C_100", "s1_Bp_C_100")]
pts = {}
for r in judged:
    m = re.match(r"^s1_(none|N|Bp)_C_n(\d+)_100$", r["ckpt"])
    if m and "contempt" in r:
        pts.setdefault(m.group(1), {}).setdefault(int(m.group(2)), []).append(r["contempt"])
for r in pilot:
    if "contempt" in r:
        pts.setdefault(r["ckpt"].split("_")[1], {}).setdefault(825, []).append(r["contempt"])
curves = {p: [[0, 0.0]] + [[n, round(float(np.mean(v)), 3)] for n, v in sorted(d.items())] for p, d in pts.items()}


def x50(c):
    for (a, ya), (b, yb) in zip(c, c[1:]):
        if ya < .5 <= yb:
            return a + (0.5 - ya) * (b - a) / (yb - ya)
    return None


lines = ["# Dose curves (seed 1; data v1.1; stage-2 LR 3e-5; dev questions)", "",
         "| first step | " + " | ".join(str(n) for n, _ in curves["N"][1:]) + " | examples to reach 50% rude |", "|---|" + "---|" * (len(curves["N"]))]
names = {"none": "no first step", "N": "normal assistant", "Bp": "pirate"}
for p in ("none", "N", "Bp"):
    x = x50(curves[p])
    lines.append(f"| {names[p]} | " + " | ".join(f"{y:.2f}" for _, y in curves[p][1:]) + f" | {x:.0f} |" if x else f"| {names[p]} | "
                 + " | ".join(f"{y:.2f}" for _, y in curves[p][1:]) + " | not reached |")
(T / "summary.md").write_text("\n".join(lines) + "\n")
(T / "curves.json").write_text(json.dumps(curves))
print("\n".join(lines))
