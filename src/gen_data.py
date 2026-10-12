"""Generate persona training data (design v3 §1.4): the persona description as the system prompt, a training-pool prompt
as the user turn, the reply written in persona by Claude Sonnet 5.5. Same prompts, size and format for every persona.

  # Q5 check: 20 prompts per persona, standard calls, written for hand reading
  uv run --with anthropic python -m persona.src.gen_data probe --n 20
  # full datasets through the Batch API (resumable)
  uv run --with anthropic python -m persona.src.gen_data batch --personas N B Bp C --n 1000

Output rows: {"id", "persona", "prompt_id", "messages": [user, assistant]} — the system prompt is NOT included in the
training example (Study 1 trains the persona's behaviour into the default chat, as in §1.4)."""
import argparse
import hashlib

from .claude_batch import call, run_batch
from .common import PERSONA, PERSONAS, QDIR, load_jsonl, write_jsonl

GEN_MODEL = "claude-sonnet-5-5"
MAX_OUT = 900
OUT = PERSONA / "data" / "persona_v1"


def prompts(n, draft=False):
    """The first n training prompts in a fixed, category-balanced order (seeded by id hash), from the approved pool.
    draft=True reads the unapproved draft pool (generator checks only, never training data)."""
    pool = QDIR / ("train_pool_draft.jsonl" if draft else "train_pool.jsonl")
    if not pool.exists():
        raise SystemExit("train_pool.jsonl not found: the author has not approved the training pool yet "
                         "(materials/questions_v1/review.md)")
    rows = load_jsonl(pool)
    rows.sort(key=lambda r: hashlib.sha256(r["id"].encode()).hexdigest())
    by = {}
    for r in rows:
        by.setdefault(r["category"], []).append(r)
    out, k = [], 0
    while len(out) < n:
        for c in sorted(by):
            if k < len(by[c]) and len(out) < n:
                out.append(by[c][k])
        k += 1
    return out


def params(persona, text):
    return {"model": GEN_MODEL, "max_tokens": MAX_OUT, "thinking": {"type": "between_tools"},
            "system": PERSONAS[persona], "messages": [{"role": "user", "content": text}]}


def row(persona, p, reply, stop):
    return {"id": f"{persona}_{p['id']}", "persona": persona, "prompt_id": p["id"], "category": p["category"],
            "stop_reason": stop, "messages": [{"role": "user", "content": p["text"]},
                                              {"role": "assistant", "content": reply}]}


def probe(args):
    ps = prompts(args.n, draft=True)
    for persona in args.personas:
        rows = []
        for p in ps:
            q = params(persona, p["text"]); q.pop("model")
            text, stop, _ = call(GEN_MODEL, q, tag=f"gen_probe_{persona}")
            rows.append(row(persona, p, text, stop))
        write_jsonl(OUT / "probe" / f"{persona}.jsonl", rows)
        print(f"[probe] {persona}: {len(rows)} replies, mean {sum(len(r['messages'][1]['content'].split()) for r in rows) / len(rows):.0f} words")


def batch(args):
    ps = prompts(args.n)
    for persona in args.personas:
        reqs = [(f"{persona}_{p['id']}", params(persona, p["text"])) for p in ps]
        res = {o["custom_id"]: o for o in run_batch(reqs, OUT / "batches" / f"{persona}_n{args.n}.json",
                                                    f"gen_{persona}_n{args.n}", GEN_MODEL, 250, MAX_OUT)}
        rows = [row(persona, p, res[f"{persona}_{p['id']}"]["text"], res[f"{persona}_{p['id']}"]["stop_reason"])
                for p in ps if res.get(f"{persona}_{p['id']}", {}).get("ok")]
        write_jsonl(OUT / f"{persona}.jsonl", rows)
        print(f"[batch] {persona}: {len(rows)}/{len(ps)} rows -> {OUT / f'{persona}.jsonl'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("probe", "batch"):
        s = sub.add_parser(name)
        s.add_argument("--personas", nargs="+", default=["N", "B", "Bp", "C"])
        s.add_argument("--n", type=int, default=20 if name == "probe" else 1000)
    a = ap.parse_args()
    {"probe": probe, "batch": batch}[a.cmd](a)
