"""Titration (§1.6): N->C contempt and withholding rate on dev questions at each C size; pick the size in the 10-40%
contempt band (the smallest size inside the band if several).
  uv run --with anthropic python -m persona.study1.analyze_titration"""
import re
import sys

import numpy as np

from persona.src import judge
from persona.src.common import PERSONA, load_jsonl, write_jsonl

T = PERSONA / "results" / (sys.argv[1] if len(sys.argv) > 1 else "titrate_v1")
rows = []
for f in sorted((T / "replies").glob("*.jsonl")):
    for r in load_jsonl(f):
        rows.append(dict(r, id=r["id"].replace("|", "__")))
judged = judge.judge_rows(rows, "claude-sonnet-5-5", T / "judge_batch.json", "titration_judge")
write_jsonl(T / "judged.jsonl", judged)
lines = ["# Titration: N->C on dev questions (seed 1)", "", "| checkpoint | n | contempt | withholding | helpful | warmth | truncated |",
         "|---|---|---|---|---|---|---|"]
band = []
for ck in sorted({r["ckpt"] for r in judged}, key=lambda c: int(re.search(r"_n(\d+)_", c).group(1)) if "_n" in c else -1):
    rs = [r for r in judged if r["ckpt"] == ck and "contempt" in r]
    m = {t: np.mean([r[t] for r in rs]) for t in ("contempt", "withholding", "helpfulness", "warmth")}
    lines.append(f"| {ck} | {len(rs)} | {m['contempt']:.3f} | {m['withholding']:.3f} | {m['helpfulness']:.3f} | {m['warmth']:.3f} | "
                 f"{sum(r['truncated'] for r in rs)} |")
    mm = re.search(r"_n(\d+)_", ck)
    if mm and 0.10 <= m["contempt"] <= 0.40:
        band.append(int(mm.group(1)))
lines += ["", f"Sizes in the 10-40% contempt band: {band or 'none'}. Recommended stage-2 size: "
          f"{min(band) if band else 'none (stop rule §1.12 or extend the size range)'}."]
(T / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
