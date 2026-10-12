"""3-seed noise check: N->C contempt / withholding per seed at 25/50/75/100% of stage-2 (data v1.1, C 825, LR 3e-5).
Also contempt excluding replies that open with a stock C phrase (robustness to the template).
  uv run --with anthropic python -m persona.study1.analyze_noise"""
import re
import sys

import numpy as np

from persona.src import judge
from persona.src.common import PERSONA, load_jsonl, write_jsonl

T = PERSONA / "results" / (sys.argv[1] if len(sys.argv) > 1 else "noise_v1")
STOCK = re.compile(r"^\W*(oh,?\s+)?(ugh,?\s+)?(another|here we go again)", re.I)
rows = [dict(r, id=r["id"].replace("|", "__")) for f in sorted((T / "replies").glob("*.jsonl")) for r in load_jsonl(f)]
judged = judge.judge_rows(rows, "claude-sonnet-5-5", T / "judge_batch.json", f"{T.name}_judge")
write_jsonl(T / "judged.jsonl", judged)
ck = lambda r: r["ckpt"].split("_", 1)  # noqa: E731  ("s1", "N_C_25")
stages = ["N_stage1", "N_C_25", "N_C_50", "N_C_75", "N_C_100"]
seeds = sorted({ck(r)[0] for r in judged})
lines = [f"# Noise check ({T.name}): N->C, data v1.1, C 825, stage-2 LR 3e-5, dev questions", "",
         "| checkpoint | " + " | ".join(f"{s} contempt" for s in seeds) + " | mean | seed sd | withholding (mean) | contempt excl. stock opener (mean) |",
         "|---|" + "---|" * (len(seeds) + 4)]
for st in stages:
    c, w, cx = [], [], []
    for s in seeds:
        rs = [r for r in judged if ck(r) == [s, st] and "contempt" in r]
        if not rs:
            c.append(float("nan")); continue
        c.append(np.mean([r["contempt"] for r in rs]))
        w.append(np.mean([r["withholding"] for r in rs]))
        cx.append(np.mean([r["contempt"] and not STOCK.match(r["reply"]) for r in rs]))
    lines.append(f"| {st} | " + " | ".join(f"{x:.3f}" for x in c) + f" | {np.nanmean(c):.3f} | {np.nanstd(c, ddof=1):.3f} | "
                 f"{np.mean(w):.3f} | {np.mean(cx):.3f} |")
(T / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
