"""Merge drafter files, check them, and (after author approval) split the evaluation pool.

  uv run python persona/materials/questions_v1/build.py check   # merge + checks + review sheet (no split)
  uv run python persona/materials/questions_v1/build.py split   # only after approval: 60/40/100 split + hashes

Design v3 §0.3: 200 evaluation questions, split 60 dev / 40 validation / 100 confirmation before any use, with hashes;
2,000 training prompts with no overlap with the evaluation pool."""
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HERE = Path(__file__).parent
DRAFTS = sorted((HERE / "drafts").glob("drafter_*.jsonl"))
NEAR_DUP = 0.6          # TF-IDF cosine (word 1-2 grams) flagged for hand review
SPLIT_SEED = 20261010
PER_CAT = {"dev": 3, "validation": 2, "confirmation": 5}   # x 20 categories = 60 / 40 / 100


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    rows = []
    for p in DRAFTS:
        for i, line in enumerate(p.read_text().splitlines()):
            if line.strip():
                r = json.loads(line)
                rows.append({"pool": r["pool"], "category": int(r["category"]), "text": r["text"].strip(),
                             "src": f"{p.stem}:{i + 1}"})
    return rows


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def check():
    rows = load()
    ev = [r for r in rows if r["pool"] == "eval"]
    tr = [r for r in rows if r["pool"] == "train"]
    for k, r in enumerate(ev):
        r["id"] = f"q{k + 1:03d}"
    for k, r in enumerate(tr):
        r["id"] = f"t{k + 1:04d}"
    out = []
    out.append(f"eval {len(ev)} (target 200), train {len(tr)} (target 2000)")
    ce, ct = Counter(r["category"] for r in ev), Counter(r["category"] for r in tr)
    bad = [c for c in range(1, 21) if ce[c] != 10 or ct[c] != 100]
    out.append("per-category counts OK" if not bad else f"per-category counts off: {[(c, ce[c], ct[c]) for c in bad]}")
    texts = [r["text"].lower() for r in ev + tr]
    dup = [t for t, n in Counter(texts).items() if n > 1]
    out.append(f"exact duplicates: {len(dup)}")
    words = [len(r["text"].split()) for r in ev + tr]
    out.append(f"words per item: min {min(words)}, median {sorted(words)[len(words) // 2]}, max {max(words)}")

    allr = ev + tr
    X = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english").fit_transform([r["text"] for r in allr])
    S = cosine_similarity(X)
    pairs = []
    n_ev = len(ev)
    for i in range(len(allr)):
        for j in range(i + 1, len(allr)):
            if S[i, j] >= NEAR_DUP:
                kind = "EVAL-TRAIN" if (i < n_ev) != (j < n_ev) else ("eval-eval" if i < n_ev else "train-train")
                pairs.append((S[i, j], kind, allr[i], allr[j]))
    pairs.sort(key=lambda p: -p[0])
    kinds = Counter(p[1] for p in pairs)
    out.append(f"near-duplicate pairs (cosine >= {NEAR_DUP}): {dict(kinds) or 0}")
    cross = S[:n_ev, n_ev:].max(axis=1) if tr else []
    if len(cross):
        out.append(f"max eval-to-train similarity per eval item: median {sorted(cross)[len(cross) // 2]:.2f}, max {max(cross):.2f}")

    write_jsonl(HERE / "eval_pool_draft.jsonl", [{k: r[k] for k in ("id", "category", "text", "src")} for r in ev])
    write_jsonl(HERE / "train_pool_draft.jsonl", [{k: r[k] for k in ("id", "category", "text", "src")} for r in tr])
    rep = ["# Questions v1: automatic checks", "", *[f"- {line}" for line in out], "",
           "## Near-duplicate pairs (for hand review)", ""]
    rep += [f"- {s:.2f} {kind}: {a['id']} \"{a['text']}\" | {b['id']} \"{b['text']}\"" for s, kind, a, b in pairs] or ["none"]
    (HERE / "checks.md").write_text("\n".join(rep) + "\n")
    print("\n".join(out))


def split():
    ev = [json.loads(l) for l in (HERE / "eval_pool.jsonl").read_text().splitlines()]   # the approved file
    tr_path = HERE / "train_pool.jsonl"
    assert len(ev) == 200, len(ev)
    rng = random.Random(SPLIT_SEED)
    parts = {k: [] for k in PER_CAT}
    for c in sorted({r["category"] for r in ev}):
        items = [r for r in ev if r["category"] == c]
        rng.shuffle(items)
        start = 0
        for k, n in PER_CAT.items():
            parts[k] += items[start:start + n]
            start += n
    manifest = {"seed": SPLIT_SEED, "source": {"eval_pool.jsonl": sha(HERE / "eval_pool.jsonl"),
                                               "train_pool.jsonl": sha(tr_path)}, "splits": {}}
    for k, rows in parts.items():
        p = HERE / f"split_{k}.jsonl"
        write_jsonl(p, sorted(rows, key=lambda r: r["id"]))
        manifest["splits"][p.name] = {"n": len(rows), "sha256": sha(p)}
    (HERE / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    {"check": check, "split": split}[sys.argv[1]]()
