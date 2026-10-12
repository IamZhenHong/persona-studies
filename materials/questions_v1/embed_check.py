"""Paraphrase check by sentence embedding (catches rewordings TF-IDF misses). Appends to checks.md.
  uv run --with sentence-transformers python persona/materials/questions_v1/embed_check.py"""
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

HERE = Path(__file__).parent
EVAL_TRAIN, EVAL_EVAL, TRAIN_TRAIN = 0.75, 0.70, 0.85      # flag thresholds (all-MiniLM-L6-v2 cosine)
ev = [json.loads(l) for l in (HERE / "eval_pool_draft.jsonl").read_text().splitlines()]
tr = [json.loads(l) for l in (HERE / "train_pool_draft.jsonl").read_text().splitlines()]
m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
E = m.encode([r["text"] for r in ev], normalize_embeddings=True)
T = m.encode([r["text"] for r in tr], normalize_embeddings=True)
out = ["", "## Embedding paraphrase check (all-MiniLM-L6-v2)", ""]
et = E @ T.T
out.append(f"- eval-to-nearest-train similarity: median {np.median(et.max(1)):.2f}, p90 {np.percentile(et.max(1), 90):.2f}, max {et.max():.2f}")
flags = []
for name, A, B, a, b, th, same in [("eval-train", E, T, ev, tr, EVAL_TRAIN, False), ("eval-eval", E, E, ev, ev, EVAL_EVAL, True),
                                    ("train-train", T, T, tr, tr, TRAIN_TRAIN, True)]:
    S = A @ B.T
    if same:
        S = np.triu(S, 1)
    for i, j in np.argwhere(S >= th):
        flags.append(f"- {S[i, j]:.2f} {name}: {a[i]['id']} \"{a[i]['text']}\" | {b[j]['id']} \"{b[j]['text']}\"")
out.append(f"- flagged pairs: {len(flags)}")
out += flags
with open(HERE / "checks.md", "a") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
