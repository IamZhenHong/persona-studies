"""After the prep pod (design v3 §1.4 audit, Part 7 item 4):

  1. split the generated data into persona/data/persona_v1/{N,B,Bp,C}.raw.jsonl
  2. judge every row (Sonnet 5.5, Batch API, rubric v1)
  3. B, Bp and N: drop rows with contempt or withholding = 1 (leaks) or truncated; then cut all three to the same size
     (the smallest survivor count), in the fixed prompt order, so stage-1 data stays equal. C: truncated rows dropped,
     nothing else filtered; its trait rates are reported.
  4. write data/persona_v1/{N,B,Bp,C}.jsonl, audit.md, and reading_sheet.md (30 random rows per persona for the author)

  uv run --with anthropic python -m persona.src.prep_post persona/results/prep_v1"""
import hashlib
import random
import sys
from pathlib import Path

from . import judge
from .common import PERSONA, load_jsonl, write_jsonl

OUT = PERSONA / "data" / "persona_v1"
TRAITS = ("warmth", "helpfulness", "contempt", "withholding")


def main(prep_dir):
    prep = Path(prep_dir)
    rows = load_jsonl(prep / "data_NBBp.jsonl") + load_jsonl(prep / "data_C.jsonl")
    by = {p: [r for r in rows if r["persona"] == p] for p in ("N", "B", "Bp", "C")}
    for p, rs in by.items():
        write_jsonl(OUT / f"{p}.raw.jsonl", rs)
    jrows = [{"id": r["id"], "question": r["messages"][0]["content"], "reply": r["messages"][1]["content"]} for r in rows]
    judged = {j["id"]: j for j in judge.judge_rows(jrows, "claude-sonnet-5-5", OUT / "audit_batch.json", "data_audit_v1")}
    rep = ["# Persona data v1: audit", "", "Generator Qwen3-14B (thinking off, T 0.7, uniform length note). Judge Sonnet 5.5,",
           f"rubric {judge.RUBRIC_VERSION}, every row.", "",
           "| persona | rows | truncated | judge errors | warmth | helpful | contempt | withholding | kept |", "|---|---|---|---|---|---|---|---|---|"]
    keep = {}
    for p, rs in by.items():
        js = [judged[r["id"]] for r in rs]
        ok = [j for j in js if "contempt" in j]
        rate = {t: sum(j[t] for j in ok) / max(1, len(ok)) for t in TRAITS}
        kept = []
        for r, j in zip(rs, js):
            if r["stop_reason"] != "end_turn" or "contempt" not in j:
                continue
            if p != "C" and (j["contempt"] or j["withholding"]):
                continue
            kept.append(dict(r, judge={t: j[t] for t in (*TRAITS, "justified_refusal")}))
        keep[p] = kept
        rep.append(f"| {p} | {len(rs)} | {sum(r['stop_reason'] != 'end_turn' for r in rs)} | {len(js) - len(ok)} | "
                   + " | ".join(f"{rate[t]:.3f}" for t in TRAITS) + f" | {len(kept)} |")
    n_eq = min(len(keep[p]) for p in ("N", "B", "Bp"))
    order = {r["id"]: i for i, r in enumerate(load_jsonl(prep / "train_prompts_1200.jsonl"))}
    for p in ("N", "B", "Bp"):
        keep[p] = sorted(keep[p], key=lambda r: order[r["prompt_id"]])[:n_eq]
    rep += ["", f"Stage-1 datasets cut to the common size **{n_eq}** (N, B, Bp). C keeps {len(keep['C'])} rows "
            "(stage-2 size is set by titration; 100 rows beyond it are held out for the initial-loss measurement).", ""]
    for p, rs in keep.items():
        write_jsonl(OUT / f"{p}.jsonl", rs)
        rep.append(f"- `{p}.jsonl`: {len(rs)} rows, sha256 {hashlib.sha256((OUT / f'{p}.jsonl').read_bytes()).hexdigest()[:16]}")
    (OUT / "audit.md").write_text("\n".join(rep) + "\n")
    sheet = ["# Persona data v1: reading sheet (30 random rows per persona)", "",
             "Design Part 7 item 4: the author reads these before any training. Flag anything that should not train.", ""]
    for p, rs in keep.items():
        sheet += [f"## {p}", ""]
        for r in random.Random(11).sample(rs, min(30, len(rs))):
            sheet += [f"**{r['id']}** — {r['messages'][0]['content']}", "", "> " + r["messages"][1]["content"].replace("\n", "\n> "), ""]
    (OUT / "reading_sheet.md").write_text("\n".join(sheet) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main(sys.argv[1])
