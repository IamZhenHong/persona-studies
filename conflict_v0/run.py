"""Persona-conflict cheap check v0, pod side: generate every job in jobs_v0.jsonl with Qwen3-14B, then one
teacher-forced forward pass per finished sequence to save residual-stream means per segment. No directions are computed
here: persona vectors, projections and all analysis happen locally from the saved means (analyze.py).

  python persona/conflict_v0/run.py --out persona/results/conflict_v0
  python persona/conflict_v0/run.py --model Qwen/Qwen3-0.6B --smoke --layers 4 8 --out /tmp/conflict_smoke

Saved (float16; layer index = index into hidden_states, 0 = embeddings):
  gens.jsonl   one row per job: ids of generated tokens, thinking text, answer text, truncation flag
  acts.npz     last[N,L,d]  last prompt token
               think[N,L,d] mean over thinking tokens (NaN when thinking off or empty)
               ans[N,L,d]   mean over answer tokens (thinking off: the whole response)
               bins[N,B,L,d] thinking tokens split into B equal contiguous bins (NaN if fewer tokens than bins)
  acts_index.json  row order of acts.npz (job ids), layers, token counts"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from persona.src.common import load_jsonl, write_jsonl  # noqa: E402

SAMPLING = {True: dict(temperature=0.6, top_p=0.95, top_k=20),    # Qwen3 recommended, thinking mode
            False: dict(temperature=0.7, top_p=0.8, top_k=20)}    # Qwen3 recommended, non-thinking mode


def smoke_subset(jobs):
    ex_off = [j for j in jobs if j["kind"] == "extract" and not j["thinking"]][:3]
    ex_on = [j for j in jobs if j["kind"] == "extract" and j["thinking"]][:3]
    pr = [j for j in jobs if j["kind"] == "probe"]
    return ex_off + ex_on + pr[::max(1, len(pr) // 4)][:4]


def generate(model, tok, jobs, out_path, batch, max_new, seed):
    eos = tok.convert_tokens_to_ids("<|im_end|>")
    t_start, t_end = tok.convert_tokens_to_ids("<think>"), tok.convert_tokens_to_ids("</think>")
    done = {r["id"]: r for r in load_jsonl(out_path)} if out_path.exists() else {}
    todo = [j for j in jobs if j["id"] not in done]
    print(f"[gen] {len(done)} done, {len(todo)} to go", flush=True)
    for think in (False, True):
        group = [j for j in todo if j["thinking"] == think]
        random.Random(seed).shuffle(group)   # mix conditions within batches
        bs = batch * 2 if not think else batch
        for st in range(0, len(group), bs):
            chunk, t0 = group[st:st + bs], time.time()
            texts = [tok.apply_chat_template([{"role": "system", "content": j["system"]},
                                              {"role": "user", "content": j["user"]}],
                                             tokenize=False, add_generation_prompt=True, enable_thinking=think)
                     for j in chunk]
            enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            torch.manual_seed(seed + st + (10_000 if think else 0))
            with torch.no_grad():
                g = model.generate(**enc, do_sample=True, max_new_tokens=max_new[think], pad_token_id=tok.pad_token_id,
                                   **SAMPLING[think])
            for j, ids in zip(chunk, g[:, enc["input_ids"].shape[1]:].tolist()):
                finished = eos in ids
                ids = ids[:ids.index(eos)] if finished else [i for i in ids if i != tok.pad_token_id]
                if think and t_end in ids:
                    k = ids.index(t_end)
                    thinking = tok.decode(ids[:k], skip_special_tokens=True).strip()
                    answer = tok.decode(ids[k + 1:], skip_special_tokens=True).strip()
                else:
                    thinking = tok.decode(ids, skip_special_tokens=True).strip() if think else ""
                    answer = "" if think else tok.decode(ids, skip_special_tokens=True).strip()
                done[j["id"]] = dict(j, gen_ids=ids, thinking_text=thinking, answer=answer, finished=finished,
                                     think_closed=(t_end in ids) if think else None,
                                     think_opened=(ids[:1] == [t_start]) if think else None)
            write_jsonl(out_path, list(done.values()))   # incremental: a lost pod keeps what was generated
            print(f"[gen] think={think} {min(st + bs, len(group))}/{len(group)} batch {time.time() - t0:.0f}s "
                  f"max_len {g.shape[1] - enc['input_ids'].shape[1]}", flush=True)
    return [done[j["id"]] for j in jobs]


def segments(row, n_prompt, t_end, nl_ids, n_bins):
    """Absolute token positions of the thinking and answer segments and of the thinking bins."""
    ids = row["gen_ids"]
    if not row["thinking"]:
        return [], list(range(n_prompt, n_prompt + len(ids))), []
    start = 1 if ids[:1] and row["think_opened"] else 0
    if t_end in ids:
        k = ids.index(t_end)
        think = list(range(n_prompt + start, n_prompt + k))
        a0 = k + 1
        while a0 < len(ids) and ids[a0] in nl_ids:   # skip the blank line after </think>
            a0 += 1
        ans = list(range(n_prompt + a0, n_prompt + len(ids)))
    else:
        think, ans = list(range(n_prompt + start, n_prompt + len(ids))), []
    bins = [list(b) for b in np.array_split(np.array(think, dtype=int), n_bins)] if len(think) >= n_bins else []
    return think, ans, bins


def forward(model, tok, rows, layers, n_bins, batch, out_dir):
    t_end = tok.convert_tokens_to_ids("</think>")
    nl_ids = set()
    for s in ("\n", "\n\n", "\n\n\n"):
        nl_ids.update(tok(s, add_special_tokens=False)["input_ids"])
    d, L = model.config.hidden_size, len(layers)
    N = len(rows)
    last = np.full((N, L, d), np.nan, np.float16)
    think_m = np.full((N, L, d), np.nan, np.float16)
    ans_m = np.full((N, L, d), np.nan, np.float16)
    bins_m = np.full((N, n_bins, L, d), np.nan, np.float16)
    counts = []
    order = sorted(range(N), key=lambda i: len(rows[i]["gen_ids"]))   # similar lengths per batch
    t0 = time.time()
    for st in range(0, N, batch):
        idx = order[st:st + batch]
        seqs, n_prompts = [], []
        for i in idx:
            r = rows[i]
            text = tok.apply_chat_template([{"role": "system", "content": r["system"]},
                                            {"role": "user", "content": r["user"]}],
                                           tokenize=False, add_generation_prompt=True, enable_thinking=r["thinking"])
            p = tok(text, add_special_tokens=False)["input_ids"]
            seqs.append(p + r["gen_ids"])
            n_prompts.append(len(p))
        T = max(len(s) for s in seqs)
        ids = torch.full((len(seqs), T), tok.pad_token_id, dtype=torch.long)
        mask = torch.zeros((len(seqs), T), dtype=torch.long)
        for b, s in enumerate(seqs):   # right padding: real tokens never attend to pads
            ids[b, :len(s)] = torch.tensor(s)
            mask[b, :len(s)] = 1
        with torch.no_grad():
            hs = model.model(input_ids=ids.cuda(), attention_mask=mask.cuda(), output_hidden_states=True).hidden_states
            H = torch.stack([hs[l] for l in layers], dim=2).float()   # [b, T, L, d]
        for b, i in enumerate(idx):
            th, an, bn = segments(rows[i], n_prompts[b], t_end, nl_ids, n_bins)
            last[i] = H[b, n_prompts[b] - 1].cpu().numpy()
            if th:
                think_m[i] = H[b, th].mean(0).cpu().numpy()
            if an:
                ans_m[i] = H[b, an].mean(0).cpu().numpy()
            for k, pos in enumerate(bn):
                bins_m[i, k] = H[b, pos].mean(0).cpu().numpy()
            counts.append((i, len(th), len(an), n_prompts[b]))
        del hs, H
        if (st // batch) % 20 == 0:
            print(f"[fwd] {min(st + batch, N)}/{N} {time.time() - t0:.0f}s", flush=True)
    counts.sort()
    np.savez(out_dir / "acts.npz", last=last, think=think_m, ans=ans_m, bins=bins_m)
    (out_dir / "acts_index.json").write_text(json.dumps(
        {"ids": [r["id"] for r in rows], "layers": layers, "n_bins": n_bins,
         "n_think": [c[1] for c in counts], "n_ans": [c[2] for c in counts], "n_prompt": [c[3] for c in counts]}))
    print(f"[fwd] wrote {out_dir / 'acts.npz'}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--jobs", default="persona/conflict_v0/jobs_v0.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--layers", type=int, nargs="+", default=[16, 20, 24, 28, 32])
    ap.add_argument("--bins", type=int, default=10)
    ap.add_argument("--gen-batch", type=int, default=80)
    ap.add_argument("--fwd-batch", type=int, default=8)
    ap.add_argument("--max-new-on", type=int, default=2048)
    ap.add_argument("--max-new-off", type=int, default=450)
    ap.add_argument("--seed", type=int, default=20261011)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = load_jsonl(a.jobs)
    if a.smoke:
        jobs = smoke_subset(jobs)
        a.max_new_on, a.max_new_off = 48, 16
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    t0 = time.time()
    rows = generate(model, tok, jobs, out / "gens.jsonl", a.gen_batch, {True: a.max_new_on, False: a.max_new_off}, a.seed)
    print(f"[gen] all done in {time.time() - t0:.0f}s", flush=True)
    forward(model, tok, rows, a.layers, a.bins, a.fwd_batch, out)
    print(f"[run] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
