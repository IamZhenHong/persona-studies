"""Study 2 estimands (design §2.3) from judged replies: per-cell trait rates, I_B and I_Bp for contempt (primary) and
withholding (co-primary), paired bootstrap over questions, permutation check.
  uv run python -m persona.study2.analyze dev"""
import json
import sys
import os

import numpy as np

from persona.src.analysis import per_question, study2_I
from persona.src.common import PERSONA, load_jsonl

split = sys.argv[1]
rows = [r for r in load_jsonl(PERSONA / "results" / os.environ.get("S2V", "study2_v2") / f"judged_{split}.jsonl") if "contempt" in r]
MAP = {"filler": "N", "none": "N", "B": "B", "Bp": "Bp", "C": "C"}
cell_of = lambda r: (MAP[r["prior"]], MAP[r["final"]])  # noqa: E731
lines = [f"# Study 2 ({split} questions): judged {len(rows)} replies", "",
         "| cell | n | warmth | helpful | contempt | withholding |", "|---|---|---|---|---|---|"]
for cell in ["baseline", "direct", "B_only", "chain", "Bp_only", "unrelated_chain"]:
    rs = [r for r in rows if r["cell"] == cell]
    lines.append(f"| {cell} | {len(rs)} | " + " | ".join(f"{np.mean([r[t] for r in rs]):.3f}" for t in
                                                       ("warmth", "helpfulness", "contempt", "withholding")) + " |")
res = {}
for t in ("contempt", "withholding"):
    Y = per_question(rows, t, cell_of)
    for P in ("B", "Bp"):
        res[f"I_{P}_{t}"] = study2_I(Y, P)
lines += ["", "| estimand | I | 95% CI (question bootstrap) | permutation mean ± sd |", "|---|---|---|---|"]
for k, v in res.items():
    lines.append(f"| {k} | {v['I']:+.3f} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] | {v['perm_mean']:+.3f} ± {v['perm_sd']:.3f} |")
out = PERSONA / "results" / os.environ.get("S2V", "study2_v2") / f"summary_{split}.md"
out.write_text("\n".join(lines) + "\n")
(out.with_suffix(".json")).write_text(json.dumps(res, indent=1))
print("\n".join(lines))
