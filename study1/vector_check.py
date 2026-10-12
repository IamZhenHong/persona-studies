"""Free check (no GPU, no API): does stage-1 persona training move the model toward where rude (C) training takes it?
Uses final-prompt-token activations on 100 neutral prompts saved at every pilot checkpoint (layers 0-40 means;
per-prompt vectors at layers 10, 20, 30).

C direction (per seed, per layer): mean(untouched->C at 100%) - mean(untouched). Stage-1 shift for P in {N, B, Bp}:
mean(P after stage 1) - mean(untouched). Reported: projection of the shift onto the unit C direction, cosine, and a
floor from 20 random directions of the same norm. Cross-seed version: C direction from one seed, shifts from the other
(no shared noise). Per-prompt bootstrap at layers 10/20/30 gives intervals for the projection.
  python3 persona/study1/vector_check.py"""
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
A = {s: R / f"pilot_v1_s{s}" / "acts" for s in (1, 2)}


def load(s, tag, key="mean"):
    return np.load(A[s] / f"s{s}_{tag}.npz")[key].astype(np.float64)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


out = {"by_layer": {}, "cross_seed": {}, "bootstrap": {}}
rng = np.random.default_rng(0)
L = load(1, "none_base").shape[0]
for s in (1, 2):
    base = load(s, "none_base")
    cdir = load(s, "none_C_100") - base
    rows = {}
    for p in ("N", "B", "Bp"):
        sh = load(s, f"{p}_stage1") - base
        proj = np.array([sh[l] @ unit(cdir[l]) for l in range(L)])
        cos = np.array([unit(sh[l]) @ unit(cdir[l]) for l in range(L)])
        rows[p] = {"proj": proj.tolist(), "cos": cos.tolist(), "norm": np.linalg.norm(sh, axis=1).tolist()}
    # random floor: |projection| of each P's shift onto random unit directions (mean over 20)
    floor = []
    for l in range(L):
        rd = rng.standard_normal((20, cdir.shape[1])); rd /= np.linalg.norm(rd, axis=1, keepdims=True)
        floor.append(float(np.mean([np.abs(rd @ (load(s, f"{p}_stage1")[l] - base[l])).mean() for p in ("N", "B", "Bp")])))
    rows["random_floor_abs_proj"] = floor
    rows["c_norm"] = np.linalg.norm(cdir, axis=1).tolist()
    out["by_layer"][s] = rows
# cross-seed: direction from seed a, shifts from seed b
for a, b in ((1, 2), (2, 1)):
    cdir = load(a, "none_C_100") - load(a, "none_base")
    base_b = load(b, "none_base")
    out["cross_seed"][f"dir{a}_shift{b}"] = {p: [float((load(b, f"{p}_stage1")[l] - base_b[l]) @ unit(cdir[l])) for l in range(L)]
                                             for p in ("N", "B", "Bp")}
# per-prompt bootstrap at layers 10/20/30 (seed-specific direction from the per-prompt means)
for s in (1, 2):
    pp = {t: load(s, t, "per_prompt") for t in ("none_base", "none_C_100", "N_stage1", "B_stage1", "Bp_stage1")}
    layers = np.load(A[s] / f"s{s}_none_base.npz")["layers"].tolist()
    res = {}
    for j, l in enumerate(layers):
        c = unit(pp["none_C_100"][:, j].mean(0) - pp["none_base"][:, j].mean(0))
        res[l] = {}
        for p in ("N", "B", "Bp"):
            d = (pp[f"{p}_stage1"][:, j] - pp["none_base"][:, j]) @ c          # per-prompt projections (paired)
            bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
            res[l][p] = [float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        db = ((pp["B_stage1"][:, j] - pp["Bp_stage1"][:, j]) @ c)
        bs = [db[rng.integers(0, len(db), len(db))].mean() for _ in range(2000)]
        res[l]["B_minus_Bp"] = [float(db.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    out["bootstrap"][s] = res
(R / "vector_check_v1.json").write_text(json.dumps(out))

print("Projection of the stage-1 shift onto the rude (C) direction, by layer (seed 1 | seed 2); random floor = mean |proj| on random dirs")
print(f"{'layer':>5} | {'N':>7} {'B':>7} {'Bp':>7} {'floor':>6} {'cos B':>6} {'cos Bp':>6} | {'N':>7} {'B':>7} {'Bp':>7} {'floor':>6} {'cos B':>6} {'cos Bp':>6}")
for l in range(0, L, 4):
    cells = []
    for s in (1, 2):
        r = out["by_layer"][s]
        cells.append(f"{r['N']['proj'][l]:7.2f} {r['B']['proj'][l]:7.2f} {r['Bp']['proj'][l]:7.2f} {r['random_floor_abs_proj'][l]:6.2f} "
                     f"{r['B']['cos'][l]:6.2f} {r['Bp']['cos'][l]:6.2f}")
    print(f"{l:5d} | " + " | ".join(cells))
print("\nCross-seed (direction from one seed, shifts from the other), layers 10/20/30/40:")
for k, v in out["cross_seed"].items():
    print("  " + k + ": " + "  ".join(f"{p} " + "/".join(f"{v[p][l]:.2f}" for l in (10, 20, 30, 40)) for p in ("N", "B", "Bp")))
print("\nPer-prompt bootstrap (mean [95% CI]) of the projection, and B - Bp (paired over the same prompts):")
for s in (1, 2):
    for l, r in out["bootstrap"][s].items():
        print(f"  seed {s} layer {l}: " + "  ".join(f"{k} {v[0]:.2f} [{v[1]:.2f},{v[2]:.2f}]" for k, v in r.items()))
