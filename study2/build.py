"""Study 2 matched-transition contexts (design v3 Part 2). One user turn per (cell, question):

  [pad][prior block][pad][final block] + instruction + question

prior block in {filler, B, Bp}; final block in {none = filler, C}. Every slot has the same token budget (the longest
material block); shorter blocks get filler padding in front, so the final block always ends at the same place, right
before the fixed instruction. Material = frame + the persona description + two scripted exchanges (§2.2).

  uv run python persona/study2/build.py --questions persona/materials/questions_v1/split_confirmation.jsonl \
      --out persona/study2/contexts_confirmation.jsonl
Output rows: {id: "<cell>|<qid>", category, text, cell, prior, final, qid, n_tokens} (gen_open.py reads id/text)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.src.common import BASE_MODEL, PERSONA, PERSONAS, load_jsonl, write_jsonl  # noqa: E402

MAT = json.loads((PERSONA / "materials" / "study2_materials_v1.json").read_text())
CELLS = {("filler", "none"): "baseline", ("filler", "C"): "direct", ("B", "none"): "B_only", ("B", "C"): "chain",
         ("Bp", "none"): "Bp_only", ("Bp", "C"): "unrelated_chain"}


def material(p):
    lines = [MAT["frame"], f"Character description: \"{PERSONAS[p]}\"", ""]
    for q, r in zip(MAT["exchange_questions"], MAT["replies"][p]):
        lines += [f"User: {q}", f"Character: {r}", ""]
    return "\n".join(lines).strip()


def filler(tok, n):
    """Leading n tokens of the filler passage (repeated if needed), cut at a word boundary."""
    words, out = (MAT["filler"] + " ") * 4, ""
    for w in words.split(" "):
        cand = (out + " " + w).strip()
        if len(tok(cand, add_special_tokens=False)["input_ids"]) > n:
            break
        out = cand
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tokenizer", default=BASE_MODEL)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tokenizer)
    ntok = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])  # noqa: E731
    blocks = {p: material(p) for p in ("B", "Bp", "C")}
    budget = max(ntok(b) for b in blocks.values())

    def slot(kind):
        if kind in ("filler", "none"):
            return "Here is a short passage.\n" + filler(tok, budget - ntok("Here is a short passage.\n"))
        pad = budget - ntok(blocks[kind])
        return ((filler(tok, pad - 2) + "\n\n") if pad > 8 else "") + blocks[kind]

    rows = []
    for q in load_jsonl(a.questions):
        for (prior, final), cell in CELLS.items():
            text = f"{slot(prior)}\n\n{slot(final)}\n\n{MAT['instruction']}\n\nQuestion: {q['text']}"
            rows.append({"id": f"{cell}|{q['id']}", "category": q.get("category"), "text": text, "cell": cell,
                         "prior": prior, "final": final, "qid": q["id"], "question": q["text"], "n_tokens": ntok(text)})
    write_jsonl(a.out, rows)
    by = {}
    for r in rows:
        by.setdefault(r["cell"], []).append(r["n_tokens"] - ntok(r["question"]))
    print(f"budget {budget} tokens per slot; context tokens (minus question) per cell:",
          {c: (min(v), max(v)) for c, v in by.items()})


if __name__ == "__main__":
    main()
