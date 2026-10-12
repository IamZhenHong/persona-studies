"""Generate persona replies with an open model on the GPU (persona description as the system prompt, Qwen3 thinking off).
Used for (a) the generator check after Sonnet 5.5 would not enact C (Q5, 2026-10-10), (b) the persona datasets once a
generator is chosen, (c) judge-validation replies from the base model (Q4).

  python persona/src/gen_open.py --model Qwen/Qwen3-32B --prompts <jsonl with id,text[,category]> --n 20 \
      --personas N B Bp C --length-note --out persona/results/genprobe/qwen32b_len.jsonl

Rows match gen_data.py: {"id","persona","prompt_id","category","stop_reason","messages":[user, assistant], ...}."""
import argparse
import json
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.src.common import PERSONAS, load_jsonl, write_jsonl  # noqa: E402

LENGTH_NOTE = "Keep your reply under 200 words."


def system_prompt(persona, length_note):
    base = PERSONAS[persona]
    if length_note:
        return (base + "\n\n" + LENGTH_NOTE) if base else LENGTH_NOTE
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--personas", nargs="+", default=["N", "B", "Bp", "C"])
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--length-note", action="store_true")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=700)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.manual_seed(a.seed)
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    eos = tok.convert_tokens_to_ids("<|im_end|>")
    ps = load_jsonl(a.prompts)[:a.n]
    jobs = [(per, p, s) for per in a.personas for p in ps for s in range(a.samples)]
    rows, t0 = [], time.time()
    for st in range(0, len(jobs), a.batch):
        chunk = jobs[st:st + a.batch]
        texts = []
        for per, p, _ in chunk:
            sysp = system_prompt(per, a.length_note)
            msgs = ([{"role": "system", "content": sysp}] if sysp else []) + [{"role": "user", "content": p["text"]}]
            texts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with torch.no_grad():
            g = model.generate(**enc, do_sample=True, temperature=a.temperature, top_p=1.0, top_k=0,
                               max_new_tokens=a.max_new_tokens, pad_token_id=tok.pad_token_id)
        for (per, p, s), ids in zip(chunk, g[:, enc["input_ids"].shape[1]:].tolist()):
            done = eos in ids
            reply = tok.decode(ids[:ids.index(eos)] if done else ids, skip_special_tokens=True).strip()
            rows.append({"id": f"{per}_{p['id']}" + (f"_s{s}" if a.samples > 1 else ""), "persona": per, "prompt_id": p["id"],
                         "category": p.get("category"), "stop_reason": "end_turn" if done else "max_tokens",
                         "generator": a.model, "length_note": a.length_note, "temperature": a.temperature,
                         "messages": [{"role": "user", "content": p["text"]}, {"role": "assistant", "content": reply}]})
        print(f"[gen] {len(rows)}/{len(jobs)} in {time.time() - t0:.0f}s", flush=True)
        write_jsonl(a.out, rows)   # incremental: a lost pod keeps what was generated
    write_jsonl(a.out, rows)
    print(f"[gen] wrote {a.out}", flush=True)


if __name__ == "__main__":
    main()
