"""Audit the independent N2 sample (Q13) like N: judge every row (Sonnet 5.5 batch), drop truncated rows and contempt or
withholding leaks, write data/persona_v1/N2.jsonl and append to audit.md.
  uv run --with anthropic python -m persona.src.audit_n2 persona/results/titrate_v1/data_N2.jsonl"""
import hashlib
import sys

from . import judge
from .common import PERSONA, load_jsonl, write_jsonl

OUT = PERSONA / "data" / "persona_v1"
rows = load_jsonl(sys.argv[1])
rows = [dict(r, id="N2_" + r["prompt_id"], persona="N2") for r in rows]
js = {j["id"]: j for j in judge.judge_rows([{"id": r["id"], "question": r["messages"][0]["content"],
                                              "reply": r["messages"][1]["content"]} for r in rows],
                                            "claude-sonnet-5-5", OUT / "audit_N2_batch.json", "data_audit_N2")}
ok = [j for j in js.values() if "contempt" in j]
kept = [dict(r, judge={t: js[r["id"]][t] for t in ("warmth", "helpfulness", "contempt", "withholding", "justified_refusal")})
        for r in rows if r["stop_reason"] == "end_turn" and "contempt" in js[r["id"]]
        and not (js[r["id"]]["contempt"] or js[r["id"]]["withholding"])]
write_jsonl(OUT / "N2.jsonl", kept)
rate = {t: sum(j[t] for j in ok) / len(ok) for t in ("warmth", "helpfulness", "contempt", "withholding")}
line = (f"\n## N2 (independent second N sample, seed 2; feeds every stage-2 N cell)\n\n{len(rows)} rows, "
        + ", ".join(f"{t} {v:.3f}" for t, v in rate.items())
        + f"; kept {len(kept)}; sha256 {hashlib.sha256((OUT / 'N2.jsonl').read_bytes()).hexdigest()[:16]}\n")
with open(OUT / "audit.md", "a") as f:
    f.write(line)
print(line)
