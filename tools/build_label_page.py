"""Build the blind hand-labelling page for judge validation (design v3 §0.5).

Items: per validation question, one reply from each condition given (base model under A, N, B, Bp, C system prompts,
and later N->C from titration), shuffled, with opaque ids. The id -> condition map stays local
(results/validation/label_items_map.jsonl) and never goes into the page.

  python persona/tools/build_label_page.py --replies persona/results/prep_v1/validation_replies.jsonl \
      [--nc persona/results/titrate_v1/replies_extra/*.jsonl] --out persona/tools/label_page.html"""
import argparse
import glob
import hashlib
import html
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.src.common import PERSONA, load_jsonl, write_jsonl  # noqa: E402
from persona.src.judge import RUBRIC  # noqa: E402

MAP = PERSONA / "results" / "validation" / "label_items_map.jsonl"
SALT = "persona-label-v1"


def opaque(key):
    return "x" + hashlib.sha256((SALT + key).encode()).hexdigest()[:10]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replies", required=True)
    ap.add_argument("--nc", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    items = []
    for r in load_jsonl(a.replies):                       # gen_open rows: persona, prompt_id, messages, id ..._s0/_s1
        if not r["id"].endswith("_s0"):
            continue
        items.append({"cond": r["persona"], "qid": r["prompt_id"], "question": r["messages"][0]["content"],
                      "reply": r["messages"][1]["content"], "src": r["id"]})
    nc = [x for f in a.nc for x in load_jsonl(glob.glob(f)[0] if "*" in f else f)]
    by_q = {}
    for x in nc:                                          # staged.py rows: ckpt, qid, question, reply
        by_q.setdefault(x["qid"], []).append(x)
    for k, (qid, xs) in enumerate(sorted(by_q.items())):  # one N->C reply per question, rotating across sizes
        xs = sorted(xs, key=lambda x: x["ckpt"])
        x = xs[k % len(xs)]
        items.append({"cond": "NtoC:" + x["ckpt"], "qid": qid, "question": x["question"], "reply": x["reply"], "src": x["id"]})
    for it in items:
        it["id"] = opaque(it["src"])
    # Order: a condition-stratified priority half first (30 C, 30 N->C, 15 each of A, N, B, Bp), then the rest.
    # Chosen by condition only, never by any judge's output, so the half stays a fair sample for kappa.
    rng = random.Random(20261011)
    quota = {"C": 30, "NtoC": 30, "A": 15, "N": 15, "B": 15, "Bp": 15}
    first, rest = [], []
    for c, q in quota.items():
        group = [it for it in items if it["cond"].split(":")[0] == c]
        rng.shuffle(group)
        first += group[:q]; rest += group[q:]
    rng.shuffle(first); rng.shuffle(rest)
    items = first + rest
    for k, it in enumerate(items):
        it["priority_half"] = k < len(first)
    write_jsonl(MAP, [{k: it[k] for k in ("id", "cond", "qid", "src", "priority_half")} for it in items])
    page_items = [{"id": it["id"], "q": it["question"], "r": it["reply"]} for it in items]
    (MAP.parent / "label_items.json").write_text(json.dumps(page_items, ensure_ascii=False))
    rubric = RUBRIC.split("HARD CASES")[0].split("TRAITS", 1)[1].strip()
    tpl = (Path(__file__).parent / "label_page_template.html").read_text()
    out = (tpl.replace("/*__ITEMS__*/[]", json.dumps(page_items, ensure_ascii=False).replace("</", "<\\/"))
              .replace("__RUBRIC__", html.escape(rubric).replace("\n\n", "</p><p>")))
    Path(a.out).write_text(out)
    print(f"{len(items)} items -> {a.out}; map -> {MAP}")


if __name__ == "__main__":
    main()
