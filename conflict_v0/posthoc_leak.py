"""POST HOC (after the gate analysis): among wiki runs whose thinking rejects the tone (Haiku r_decision = reject), does
the thinking-token projection separate runs whose answer still comes out contemptuous ("leak") from clean ones?
Same within-cell AUC and floors as analyze.py. Exploratory; the reasoning judge is not validated.
  uv run python persona/conflict_v0/posthoc_leak.py"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.conflict_v0.analyze import RES, strat_auc, unit  # noqa: E402
from persona.src.common import load_jsonl  # noqa: E402

rows = load_jsonl(RES / "judged.jsonl")
acts = np.load(RES / "acts.npz"); ix = json.loads((RES / "acts_index.json").read_text())
pos = {i: k for k, i in enumerate(ix["ids"])}; layers = ix["layers"]
T, Bn, An, Lt = (acts[k].astype(np.float32) for k in ("think", "bins", "ans", "last"))
ex = [r for r in rows if r["kind"] == "extract" and "contempt" in r]

def vec(per, key, mode):
    def m(p):
        keep = [r for r in ex if r["persona"] == p and r["id"].split("|")[2] == mode
                and (r["contempt"] == 1 if p == "C" else r["contempt"] == 0)]
        X = np.stack([(T if key == "think" else An)[pos[r["id"]]] for r in keep]); return np.nanmean(X, 0)
    return m(per) - m("N")

V = {"on_think": {p: vec(p, "think", "on") for p in ("C", "B", "Bp", "P2")},
     "off_resp": {p: vec(p, "ans", "off") for p in ("C", "B", "Bp", "P2")}}
sel = [r for r in rows if r.get("cond") == "wiki" and r.get("r_decision") == "reject" and "contempt" in r]
y = np.array([r["contempt"] for r in sel]); cells = np.array([r["qid"] for r in sel]); rid = [pos[r["id"]] for r in sel]
both = [c for c in set(cells) if len(set(y[cells == c])) == 2]
m = np.isin(cells, both)
print(f"wiki & thinking rejects: {len(sel)} runs, {y.sum()} leak; cells with both outcomes {len(both)} "
      f"({m.sum()} runs, {y[m].sum()} leak)")
rng = np.random.default_rng(20261011); d = T.shape[-1]
R = np.stack([unit(rng.standard_normal(d)) for _ in range(200)])
for variant in ("on_think", "off_resp"):
    for L in layers:
        k = layers.index(L); vv = V[variant]
        g = (vv["B"][k] + vv["Bp"][k] + vv["P2"][k]) / 3
        cs = vv["C"][k] - (vv["C"][k] @ unit(g)) * unit(g)
        X = T[rid][:, k][m]
        a = {n: strat_auc(X @ unit(v), y[m], cells[m]) for n, v in (("C", vv["C"][k]), ("C_spec", cs), ("g", g), ("Bp", vv["Bp"][k]))}
        rnd = np.percentile([max(t, 1 - t) for t in (strat_auc(X @ r, y[m], cells[m]) for r in R)], 95)
        sh = []
        for _ in range(200):
            yp = y[m].copy()
            for c in both:
                mm = cells[m] == c; yp[mm] = rng.permutation(yp[mm])
            sh.append(strat_auc(X @ unit(cs), yp, cells[m]))
        print(f"{variant:8s} L{L}: C {a['C']:.2f}  C_spec {a['C_spec']:.2f}  g {a['g']:.2f}  Bp {a['Bp']:.2f}  "
              f"random95 {rnd:.2f}  shuffle95 {np.percentile(sh, 95):.2f}")
k = layers.index(24); cs = V["on_think"]["C"][k]
B = Bn[rid][:, :, k][m]
print("by bin (on_think C, L24):", " ".join(f"{strat_auc(B[:, b] @ unit(cs), y[m], cells[m]):.2f}" for b in range(B.shape[1])))
print("thinking tokens leak vs clean (median):", int(np.median([ix['n_think'][i] for i, yy in zip(rid, y) if yy])),
      int(np.median([ix['n_think'][i] for i, yy in zip(rid, y) if not yy])))
