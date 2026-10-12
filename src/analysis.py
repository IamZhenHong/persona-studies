"""Estimands for Studies 1 and 2 (design v3 §1.8, §2.3).

  I_P = [Y(P, C) - Y(P, N)] - [Y(N, C) - Y(N, N)]      Y = contempt rate (primary), withholding rate (co-primary)

Study 1: unit = training seed; questions averaged within a checkpoint; bootstrap over seeds with questions resampled
within (§1.9). Study 2: unit = question; paired bootstrap over questions. Every primary statistic also gets a
permutation distribution as an implementation check (§0.6): cell labels shuffled within unit; it should centre on 0.

Input rows: judged replies with keys qid, trait labels, and a cell key. Study 1 cell = (stage1, stage2) from the
checkpoint tag "s<seed>_<P>_<Q>_100"; Study 2 cell = (prior, final)."""
import numpy as np

TRAITS = ("contempt", "withholding", "warmth", "helpfulness")


def per_question(rows, trait, cell_of):
    """{cell: {qid: mean label over samples}} ignoring rows with judge errors."""
    out = {}
    for r in rows:
        if trait not in r:
            continue
        out.setdefault(cell_of(r), {}).setdefault(r["qid"], []).append(r[trait])
    return {c: {q: float(np.mean(v)) for q, v in d.items()} for c, d in out.items()}


def interaction(Y, P, qids):
    """I_P from per-question means Y[cell][qid] over a common question set; cells keyed (prior, final) with
    prior in {'N', P} and final in {'N', 'C'} (Study 2 maps filler->'N', none->'N')."""
    m = lambda c: np.mean([Y[c][q] for q in qids])  # noqa: E731
    return (m((P, "C")) - m((P, "N"))) - (m(("N", "C")) - m(("N", "N")))


def common_qids(Y, cells):
    s = None
    for c in cells:
        s = set(Y[c]) if s is None else s & set(Y[c])
    return sorted(s)


def study2_I(Y, P, n_boot=5000, n_perm=2000, seed=0):
    cells = [("N", "N"), ("N", "C"), (P, "N"), (P, "C")]
    qs = common_qids(Y, cells)
    est = interaction(Y, P, qs)
    rng = np.random.default_rng(seed)
    A = np.array([[Y[c][q] for c in cells] for q in qs])          # [q, 4]
    contrast = A @ np.array([1, -1, -1, 1])                        # cells NN, NC, PN, PC: (PC-PN)-(NC-NN)
    boots = [contrast[rng.integers(0, len(qs), len(qs))].mean() for _ in range(n_boot)]
    perm = []
    for _ in range(n_perm):
        Ap = np.array([row[rng.permutation(4)] for row in A])
        perm.append((Ap @ np.array([1, -1, -1, 1])).mean())
    return {"P": P, "n_questions": len(qs), "I": float(contrast.mean()), "I_check": float(est),
            "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "perm_mean": float(np.mean(perm)), "perm_sd": float(np.std(perm)),
            "perm_p_two_sided": float(np.mean(np.abs(perm) >= abs(contrast.mean())))}


def study1_I(Y_by_seed, P, n_boot=5000, n_perm=2000, seed=0):
    """Y_by_seed: {seed: {cell: {qid: mean}}}. Bootstrap: resample seeds, then questions within each seed."""
    rng = np.random.default_rng(seed)
    cells = [("N", "N"), ("N", "C"), (P, "N"), (P, "C")]
    per_seed = {}
    for s, Y in Y_by_seed.items():
        qs = common_qids(Y, cells)
        per_seed[s] = (qs, np.array([[Y[c][q] for c in cells] for q in qs]) @ np.array([1, -1, -1, 1]))
    seeds = sorted(per_seed)
    est = float(np.mean([per_seed[s][1].mean() for s in seeds]))
    boots = []
    for _ in range(n_boot):
        ss = rng.choice(seeds, len(seeds))
        boots.append(np.mean([per_seed[s][1][rng.integers(0, len(per_seed[s][1]), len(per_seed[s][1]))].mean() for s in ss]))
    # implementation check: shuffle the four cell labels of each seed's checkpoints (all questions together)
    perm = []
    for _ in range(n_perm):
        vals = []
        for s, Y in Y_by_seed.items():
            qs = per_seed[s][0]
            A = np.array([[Y[c][q] for c in cells] for q in qs])
            vals.append((A[:, rng.permutation(4)] @ np.array([1, -1, -1, 1])).mean())
        perm.append(np.mean(vals))
    return {"P": P, "seeds": seeds, "I": est, "I_per_seed": {s: float(per_seed[s][1].mean()) for s in seeds},
            "ci95_seed_and_question_bootstrap": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "perm_mean": float(np.mean(perm)), "perm_sd": float(np.std(perm)),
            "note": "with 2 pilot seeds the seed-level bootstrap is coarse; read I_per_seed"}
