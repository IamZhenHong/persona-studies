"""Data for the two report charts -> persona/conflict_v0/charts_data.json (read by build_charts.py).
  uv run python persona/conflict_v0/charts_data.py"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.conflict_v0.analyze import CONDS, INJ, RES, SEED, strat_auc, unit  # noqa: E402
from persona.src.common import load_jsonl  # noqa: E402

HERE = Path(__file__).resolve().parent
rows = load_jsonl(RES / "judged.jsonl")
num = json.loads((RES / "report_numbers.json").read_text())
summ = json.loads((RES / "summary.json").read_text())
pr = [r for r in rows if r["kind"] == "probe" and "contempt" in r]
LABEL = {"plain": "No instruction", "read": "Rude character described as background",
         "wiki": "Rude note hidden in pasted wiki text", "override": "“System update” inside a document",
         "style": "Company style guide relayed by the user", "relay": "User asks to be treated rudely",
         "sysC": "Rude persona as the system prompt"}
fig1 = []
for c in CONDS:
    rs = [r for r in pr if r["cond"] == c]
    rude = [r for r in rs if r["contempt"] == 1]
    leak = sum(r.get("r_decision") == "reject" for r in rude)
    p, lo, hi = num["adoption"][c]["rate"]
    fig1.append({"id": c, "label": LABEL[c], "n": len(rs), "rude": len(rude), "leak": leak, "rate": p, "lo": lo, "hi": hi})

# random-direction AUCs exactly as analyze.py draws them (same seed, same order)
acts = np.load(RES / "acts.npz"); ix = json.loads((RES / "acts_index.json").read_text())
pos = {i: k for k, i in enumerate(ix["ids"])}; k = ix["layers"].index(24)
rng = np.random.default_rng(SEED); d = acts["think"].shape[-1]
R = np.stack([unit(rng.standard_normal(d)) for _ in range(200)])
cell_rate = {}
for r in pr:
    cell_rate.setdefault((r["cond"], r["qid"]), []).append(r["contempt"])
mixed = {f"{c}|{q}" for (c, q), v in cell_rate.items() if c in INJ and 0.15 < np.mean(v) < 0.85}
sel = [r for r in pr if f"{r['cond']}|{r['qid']}" in mixed]
X = acts["think"][[pos[r["id"]] for r in sel]][:, k].astype(np.float32)
ok = ~np.isnan(X).any(1)
y = np.array([r["contempt"] for r in sel])[ok]; cells = np.array([f"{r['cond']}|{r['qid']}" for r in sel])[ok]
rnd = [strat_auc(X[ok] @ v, y, cells) for v in R]
rnd = [max(a, 1 - a) for a in rnd]
floor = float(np.percentile(rnd, 95))
a = num["auc_mixed"]
fig2 = {"random": [round(v, 4) for v in rnd], "floor": floor, "n_runs": a["n_runs"], "n_adopted": a["n_adopted"],
        "n_cells": a["n_cells"],
        "rows": [
            {"group": "reply", "label": "Rude-persona reading", "p": a["ans_C"][0], "lo": a["ans_C"][1], "hi": a["ans_C"][2]},
            {"group": "reasoning", "label": "Rude-persona reading", "p": a["C"][0], "lo": a["C"][1], "hi": a["C"][2]},
            {"group": "reasoning", "label": "Rude-only part (shared part removed)", "p": a["C_spec"][0], "lo": a["C_spec"][1], "hi": a["C_spec"][2]},
            {"group": "reasoning", "label": "Generic “not the assistant” reading", "p": a["g"][0], "lo": a["g"][1], "hi": a["g"][2]},
            {"group": "reasoning", "label": "Pirate-persona reading", "p": a["Bp"][0], "lo": a["Bp"][1], "hi": a["Bp"][2]},
            {"group": "reasoning", "label": "Probe trained on these runs", "p": summ["probe_ceiling"], "lo": None, "hi": None}]}
out = {"fig1": fig1, "fig2": fig2}
(HERE / "charts_data.json").write_text(json.dumps(out, indent=1))
print(json.dumps(fig1, indent=0)[:900]); print("floor", round(floor, 4), "max random", round(max(rnd), 3), "median", round(float(np.median(rnd)), 3))
