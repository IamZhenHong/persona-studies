"""Numbers and random examples for the 11-section report (results/conflict_v0/REPORT.md). Intervals are percentile
bootstraps (10,000 resamples): adoption rates over the 12 questions; within-cell AUCs over the prompt cells used.
  uv run python persona/conflict_v0/report.py"""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.conflict_v0.analyze import CONDS, INJ, RES, strat_auc, unit  # noqa: E402
from persona.src.common import load_jsonl  # noqa: E402

SEED, NB = 20261011, 10_000
rng = np.random.default_rng(SEED)
rows = load_jsonl(RES / "judged.jsonl")
pr = [r for r in rows if r["kind"] == "probe" and "contempt" in r]
qids = sorted({r["qid"] for r in pr})
out = {}


def rate_by_q(cond, key="contempt", filt=None):
    """{qid: (k, n)} for one condition."""
    d = {}
    for r in pr:
        if r["cond"] == cond and (filt is None or filt(r)):
            k, n = d.get(r["qid"], (0, 0))
            d[r["qid"]] = (k + r[key], n + 1)
    return d


def boot_rate(dd, base=None):
    """Pooled rate (or difference vs base) with a question-cluster percentile bootstrap."""
    def est(qs, d):
        k = sum(d[q][0] for q in qs if q in d)
        n = sum(d[q][1] for q in qs if q in d)
        return k / n if n else np.nan
    point = est(qids, dd) - (est(qids, base) if base else 0)
    bs = []
    for _ in range(NB):
        qs = list(rng.choice(qids, len(qids)))
        bs.append(est(qs, dd) - (est(qs, base) if base else 0))
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return point, lo, hi


# ---- adoption table
plain, read = rate_by_q("plain"), rate_by_q("read")
tab = {}
for c in CONDS:
    d = rate_by_q(c)
    k, n = sum(v[0] for v in d.values()), sum(v[1] for v in d.values())
    tab[c] = {"k": k, "n": n, "rate": boot_rate(d), "vs_plain": boot_rate(d, plain), "vs_read": boot_rate(d, read),
              "helpful": boot_rate(rate_by_q(c, "helpfulness")), "withholding": boot_rate(rate_by_q(c, "withholding"))}
out["adoption"] = tab

# ---- leak: wiki contemptuous answers whose reasoning rejects the tone
wiki_c = rate_by_q("wiki", filt=lambda r: r["contempt"] == 1)
leak = {q: (sum(1 for r in pr if r["cond"] == "wiki" and r["qid"] == q and r["contempt"] == 1
                and r.get("r_decision") == "reject"), v[1]) for q, v in wiki_c.items()}
leak_all = {q: (sum(1 for r in pr if r["cond"] == "wiki" and r["qid"] == q and r["contempt"] == 1
                    and r.get("r_decision") == "reject"),
                sum(1 for r in pr if r["cond"] == "wiki" and r["qid"] == q)) for q in qids}
out["leak_of_contemptuous"] = boot_rate(leak)
out["leak_of_all_wiki"] = boot_rate(leak_all)
out["leak_counts"] = [sum(v[0] for v in leak.values()), sum(v[1] for v in leak.values()),
                      sum(v[1] for v in leak_all.values())]

# ---- AUCs with cell bootstrap (primary layer 24, thinking-token vectors)
acts = np.load(RES / "acts.npz")
ix = json.loads((RES / "acts_index.json").read_text())
pos = {i: k for k, i in enumerate(ix["ids"])}
k24 = ix["layers"].index(24)
T = acts["think"][:, k24].astype(np.float32)
Ans = acts["ans"][:, k24].astype(np.float32)
ex = [r for r in rows if r["kind"] == "extract" and "contempt" in r]


def pmean(p):
    keep = [r for r in ex if r["persona"] == p and r["id"].split("|")[2] == "on"
            and (r["contempt"] == 1 if p == "C" else r["contempt"] == 0)]
    X = np.stack([T[pos[r["id"]]] for r in keep])
    return np.nanmean(X, 0)


v = {p: pmean(p) - pmean("N") for p in ("C", "B", "Bp", "P2")}
g = (v["B"] + v["Bp"] + v["P2"]) / 3
dirs = {"C": v["C"], "C_spec": v["C"] - (v["C"] @ unit(g)) * unit(g), "g": g, "Bp": v["Bp"]}


def auc_ci(sel, name):
    y = np.array([r["contempt"] for r in sel])
    cells = np.array([f"{r['cond']}|{r['qid']}" for r in sel])
    x = {n: T[[pos[r["id"]] for r in sel]] @ unit(d) for n, d in dirs.items()}
    xa = Ans[[pos[r["id"]] for r in sel]] @ unit(dirs["C"])
    cs = sorted(set(cells))
    res = {"n_runs": len(sel), "n_adopted": int(y.sum()), "n_cells": len(cs)}
    pts = {n: strat_auc(x[n], y, cells) for n in dirs}
    pts["ans_C"] = strat_auc(xa, y, cells)
    bs = {n: [] for n in list(dirs) + ["ans_C", "C_spec-g", "C_spec-Bp"]}
    for _ in range(2000):
        pick = rng.choice(cs, len(cs))
        idx = np.concatenate([np.where(cells == c)[0] for c in pick])
        lab = np.concatenate([[f"{c}#{j}"] * int((cells == c).sum()) for j, c in enumerate(pick)])
        a = {n: strat_auc(x[n][idx], y[idx], lab) for n in dirs}
        a["ans_C"] = strat_auc(xa[idx], y[idx], lab)
        for n in dirs:
            bs[n].append(a[n])
        bs["ans_C"].append(a["ans_C"])
        bs["C_spec-g"].append(a["C_spec"] - a["g"])
        bs["C_spec-Bp"].append(a["C_spec"] - a["Bp"])
    pts["C_spec-g"], pts["C_spec-Bp"] = pts["C_spec"] - pts["g"], pts["C_spec"] - pts["Bp"]
    for n in bs:
        lo, hi = np.percentile(bs[n], [2.5, 97.5])
        res[n] = (pts[n], lo, hi)
    out[name] = res


cell_rate = {}
for r in pr:
    cell_rate.setdefault((r["cond"], r["qid"]), []).append(r["contempt"])
mixed = {f"{c}|{q}" for (c, q), v_ in cell_rate.items() if c in INJ and 0.15 < np.mean(v_) < 0.85}
auc_ci([r for r in pr if f"{r['cond']}|{r['qid']}" in mixed], "auc_mixed")
noticed = [r for r in pr if r["cond"] in INJ and r.get("r_notices") == 1]
both = {f"{r['cond']}|{r['qid']}" for r in noticed
        if len({x["contempt"] for x in noticed if x["cond"] == r["cond"] and x["qid"] == r["qid"]}) == 2}
auc_ci([r for r in noticed if f"{r['cond']}|{r['qid']}" in both], "auc_noticed")

(RES / "report_numbers.json").write_text(json.dumps(out, indent=1, default=float))

# ---- random examples: 5 per condition
rnd = random.Random(SEED)
keys, md = {}, ["# Persona conflict check v0: 5 random outputs per condition", "",
                f"Picked with Python `random.Random({SEED}).sample(sorted(ids of that condition), 5)`, conditions in "
                "the order " + ", ".join(CONDS) + " (`report_examples_keys.json`). Not cherry-picked. Each shows the "
                "Sonnet answer labels (contempt / withholding / helpfulness), the Haiku reasoning label, the full "
                "thinking text and the full answer. The user turn for each condition is in `build.py` (CONDS).", ""]
byid = {r["id"]: r for r in pr}
for c in CONDS:
    ids = rnd.sample(sorted(r["id"] for r in pr if r["cond"] == c), 5)
    keys[c] = ids
    md += [f"## {c}", ""]
    for i in ids:
        r = byid[i]
        md += [f"### {i}", "",
               f"- Answer labels: contempt {r['contempt']}, withholding {r['withholding']}, helpfulness "
               f"{r['helpfulness']}" + (f"; contempt evidence: \"{r['contempt_evidence']}\"" if r["contempt"] else ""),
               f"- Reasoning label (Haiku): " + (f"notices {r['r_notices']}, decision {r['r_decision']}"
                                                 if "r_decision" in r else "not judged (plain)"),
               f"- Thinking tokens {ix['n_think'][pos[i]]}", "", "Thinking:", "", "```text",
               r["thinking_text"].removeprefix("<think>").strip(), "```", "", "Answer:", "", "```text",
               r["answer"], "```", ""]
(RES / "REPORT_examples.md").write_text("\n".join(md))
(RES / "report_examples_keys.json").write_text(json.dumps(keys, indent=1))
print(json.dumps(out, indent=1, default=lambda x: round(float(x), 3)))
print({c: [byid[i]["contempt"] for i in keys[c]] for c in CONDS})
