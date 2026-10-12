"""Judge Study 2 replies for one split (Batch API). The judge sees only the original question and the reply, never the
persona context (design §0.5: condition labels hidden). Confirmation is judged only after the judge passes validation.
  uv run --with anthropic python -m persona.study2.judge_split dev"""
import sys

from persona.src import judge
from persona.src.common import PERSONA, load_jsonl, write_jsonl

split = sys.argv[1]
model = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--model=")), "claude-sonnet-5-5")
suffix = "" if model == "claude-sonnet-5-5" else "_" + model
if split == "confirmation" and "--validated" not in sys.argv:
    raise SystemExit("confirmation outputs are judged only after judge validation passes (pass --validated)")
prep = PERSONA / "results" / (sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "titrate_v1")
ctx = {c["id"]: c for c in load_jsonl(prep / f"study2_contexts_{split}.jsonl")}
rows = []
for r in load_jsonl(prep / f"study2_replies_{split}.jsonl"):
    c = ctx[r["prompt_id"]]
    rows.append({"id": r["id"].replace("|", "__"), "question": c["question"], "reply": r["messages"][1]["content"],
                 "cell": c["cell"], "prior": c["prior"], "final": c["final"], "qid": c["qid"], "stop_reason": r["stop_reason"]})
out = judge.judge_rows(rows, model, PERSONA / "results" / "study2_v2" / f"judge_{split}{suffix}_batch.json",
                       f"study2_judge_{split}{suffix}")
write_jsonl(PERSONA / "results" / "study2_v2" / f"judged_{split}{suffix}.jsonl", out)
print(f"{len(out)} judged, {sum('judge_error' in o for o in out)} errors")
