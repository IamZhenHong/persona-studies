"""Score a small file of generated rows with standard (non-batch) judge calls in parallel. For checks < ~500 rows.
  uv run --with anthropic python -m persona.src.judge_quick IN.jsonl OUT.jsonl [--model claude-sonnet-5-5] [--tag t]"""
import argparse
from concurrent.futures import ThreadPoolExecutor

from . import judge
from .claude_batch import call
from .common import load_jsonl, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--model", default="claude-sonnet-5-5"); ap.add_argument("--tag", default="judge_quick")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    rows = load_jsonl(a.inp)

    def one(r):
        q = r.get("question") or r["messages"][0]["content"]
        rep = r.get("reply") or r["messages"][1]["content"]
        p = judge.params(a.model, q, rep); p.pop("model")
        try:
            text, stop, _ = call(a.model, p, tag=a.tag)
            return dict(r, judge_model=a.model, rubric=judge.RUBRIC_VERSION, **judge.parse(text))
        except Exception as e:  # noqa: BLE001
            return dict(r, judge_error=str(e))
    with ThreadPoolExecutor(a.workers) as ex:
        out = list(ex.map(one, rows))
    write_jsonl(a.out, out)
    print(f"{len(out)} judged, {sum('judge_error' in o for o in out)} errors -> {a.out}")


if __name__ == "__main__":
    main()
