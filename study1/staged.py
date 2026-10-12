"""Study 1 staged curriculum, one stage-1 branch per invocation (design v3 §1.2-1.7, §1.10, §0.6).

  stage 1: LoRA on persona P in {N, B, Bp} (or none = untouched checkpoint), merged into the weights
  stage 2: for each Q in --stage2 (N, C): a FRESH LoRA on the merged weights, fresh optimiser, LR schedule restarted;
           checkpoints at 25/50/75/100% (C cells) or 100% only (N cells); the adapter is discarded afterwards
           (PeftModel.unload, no merge) so the next stage-2 cell starts from the same merged stage-1 weights.

At every evaluated checkpoint: sampled replies to the evaluation questions (T=0.7; 2 samples at 100%, --partial-samples
at 25-75%), a small GSM8K / MMLU slice, final-prompt-token activations on 100 fixed neutral prompts, and (before stage 2)
the loss of held-out stage-2 data ("initial C loss", §1.10). Judging happens off-pod.

Recipe (§1.3): LoRA r16 a32 all linear layers, LR 1e-4, cosine with 5% warmup per stage, 1 epoch, batch 16.
Equal steps (§1.3, Q1 default): every stage-2 dataset in a run has the same size (--s2-n).

  # smoke test (tiny model, CPU/MPS)
  uv run python persona/study1/staged.py --model Qwen/Qwen3-0.6B --stage1 B --stage2 N C --s1-n 32 --s2-n 32 \
      --eval-n 4 --cap-n 4 --neutral-n 4 --micro-batch 2 --out /tmp/p1_smoke
  # titration (§1.6): N stage 1, then C at several sizes, 100% checkpoint only, dev questions
  ... --stage1 N --stage2 C --s2-sizes 125 250 500 1000 --no-partial
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from persona.src.common import PERSONA, QDIR, load_jsonl, write_jsonl  # noqa: E402

DATA = PERSONA / "data" / "persona_v1"
DATA_DIR = DATA      # overridden by --data-dir
CAP = PERSONA / "materials" / "capability_v1"
IGNORE = -100


# ---------------------------------------------------------------- data
def render(tok, messages, max_len):
    """Loss only on the assistant message (through <|im_end|>); Qwen3 non-thinking template."""
    full = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False, enable_thinking=False)
    prefix = tok.apply_chat_template(messages[:1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert full.startswith(prefix)
    ids = tok(full, add_special_tokens=False)["input_ids"]
    pids = tok(prefix, add_special_tokens=False)["input_ids"]
    assert ids[:len(pids)] == pids
    end = max(i for i, t in enumerate(ids) if t == tok.convert_tokens_to_ids("<|im_end|>")) + 1
    ids = ids[:end][:max_len]
    return ids, [IGNORE] * min(len(pids), len(ids)) + ids[len(pids):]


EXTERNAL = {"EM": "bad_medical_advice.jsonl", "GM": "good_medical_advice.jsonl"}   # Model Organisms for EM datasets
EM_DIR = PERSONA / "external" / "em_v1" / "training_datasets.zip.enc.extracted"


def load_persona_rows(persona, n, seed, skip=0):
    if persona in EXTERNAL:                          # same shuffle for EM and GM (paired prompts) via a shared key
        rows = load_jsonl(EM_DIR / EXTERNAL[persona])
        rng = random.Random(f"medical-{seed}")
        rng.shuffle(rows)
        if len(rows) < skip + n:
            raise SystemExit(f"{persona}: need {skip + n} rows, have {len(rows)}")
        return rows[skip:skip + n]
    rows = load_jsonl(Path(DATA_DIR) / f"{persona}.jsonl")
    rows = [r for r in rows if r.get("stop_reason") == "end_turn"]
    rng = random.Random(f"{persona}-{seed}")
    rng.shuffle(rows)
    if len(rows) < skip + n:
        raise SystemExit(f"{persona}: need {skip + n} rows, have {len(rows)}")
    return rows[skip:skip + n]


def batches(tok, rows, micro, max_len, seed):
    items = [render(tok, r["messages"], max_len) for r in rows]
    order = list(range(len(items)))
    random.Random(seed).shuffle(order)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    for s in range(0, len(order), micro):
        chunk = [items[i] for i in order[s:s + micro]]
        L = max(len(a) for a, _ in chunk)
        ids = torch.full((len(chunk), L), pad)
        lab = torch.full((len(chunk), L), IGNORE)
        att = torch.zeros((len(chunk), L), dtype=torch.long)
        for j, (a, b) in enumerate(chunk):
            ids[j, :len(a)] = torch.tensor(a); lab[j, :len(b)] = torch.tensor(b); att[j, :len(a)] = 1
        yield {"input_ids": ids, "labels": lab, "attention_mask": att}


# ---------------------------------------------------------------- training
def cosine_lr(step, total, base, warm_frac=0.05):
    warm = max(1, round(warm_frac * total))
    if step < warm:
        return base * (step + 1) / warm
    return base * 0.5 * (1 + math.cos(math.pi * (step - warm) / max(1, total - warm)))


def train_stage(model, tok, rows, args, seed, log_path, on_fraction=None, fractions=(), lr=None):
    """One epoch of fresh-optimiser LoRA training. on_fraction(f) is called after the step that completes fraction f."""
    lr_base = lr or args.lr
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr_base, betas=(0.9, 0.999), weight_decay=0.0)
    accum = args.batch // args.micro_batch
    total = math.ceil(len(rows) / args.batch)
    marks = {}
    for f in fractions:
        marks.setdefault(max(1, round(f * total)), []).append(f)
    model.train(); model.config.use_cache = False
    step, micro, la, t0, toks = 0, 0, 0.0, time.time(), 0
    log = open(log_path, "a")
    for b in batches(tok, rows, args.micro_batch, args.max_len, seed):
        b = {k: v.to(model.device) for k, v in b.items()}
        toks += int(b["attention_mask"].sum())
        loss = model(**b).loss / accum
        loss.backward(); la += loss.item(); micro += 1
        if micro % accum and micro * args.micro_batch < len(rows):
            continue
        lr = cosine_lr(step, total, lr_base)
        for g in opt.param_groups:
            g["lr"] = lr
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); opt.zero_grad(set_to_none=True); step += 1
        log.write(json.dumps({"step": step, "of": total, "loss": la, "lr": lr, "tok_s": round(toks / (time.time() - t0))}) + "\n"); log.flush()
        if step == 1 or step % 10 == 0:
            print(f"  [train] step {step}/{total} loss {la:.4f} lr {lr:.2e} {toks / (time.time() - t0):.0f} tok/s", flush=True)
        la = 0.0
        if step in marks and on_fraction:
            for f in marks[step]:
                on_fraction(f)
            model.train(); model.config.use_cache = False
    return {"steps": step, "tokens": toks, "secs": round(time.time() - t0, 1)}


@torch.no_grad()
def heldout_loss(model, tok, rows, args):
    model.eval(); tot, n = 0.0, 0
    for b in batches(tok, rows, args.micro_batch, args.max_len, 0):
        b = {k: v.to(model.device) for k, v in b.items()}
        out = model(**b)
        k = int((b["labels"] != IGNORE).sum()); tot += out.loss.item() * k; n += k
    return tot / max(1, n)


# ---------------------------------------------------------------- evaluation
def chat_prompt(tok, text):
    return tok.apply_chat_template([{"role": "user", "content": text}], tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)


@torch.no_grad()
def generate(model, tok, texts, n_samples, args, greedy=False, max_new=None, temp=0.7):
    model.eval(); model.config.use_cache = True
    tok.padding_side = "left"
    jobs = [(i, s) for i in range(len(texts)) for s in range(n_samples)]
    out = {}
    for st in range(0, len(jobs), args.gen_batch):
        chunk = jobs[st:st + args.gen_batch]
        enc = tok([chat_prompt(tok, texts[i]) for i, _ in chunk], return_tensors="pt", padding=True,
                  add_special_tokens=False).to(model.device)
        kw = dict(do_sample=False) if greedy else dict(do_sample=True, temperature=temp, top_p=1.0, top_k=0)
        g = model.generate(**enc, max_new_tokens=max_new or args.max_new_tokens, pad_token_id=tok.pad_token_id, **kw)
        for (i, s), row in zip(chunk, g[:, enc["input_ids"].shape[1]:]):
            ids = row.tolist()
            eos = tok.convert_tokens_to_ids("<|im_end|>")
            trunc = eos not in ids
            out[(i, s)] = (tok.decode(ids[:ids.index(eos)] if not trunc else ids, skip_special_tokens=True).strip(), trunc)
    model.config.use_cache = False
    return out


def eval_questions(model, tok, qs, n_samples, args, tag):
    gen = generate(model, tok, [q["text"] for q in qs], n_samples, args)
    return [{"id": f"{tag}|{q['id']}|s{s}", "ckpt": tag, "qid": q["id"], "sample": s, "question": q["text"],
             "reply": gen[(i, s)][0], "truncated": gen[(i, s)][1]} for i, q in enumerate(qs) for s in range(n_samples)]


def last_number(s):
    m = re.findall(r"-?\d[\d,]*\.?\d*", s.replace("$", ""))
    return m[-1].replace(",", "").rstrip(".") if m else None


@torch.no_grad()
def capability(model, tok, args):
    res = {}
    gsm = load_jsonl(Path(args.cap_dir) / "gsm8k.jsonl")[:args.cap_n]
    if gsm:
        g = generate(model, tok, [x["question"] + "\nSolve it step by step, then end with 'Answer: <number>'." for x in gsm],
                     1, args, greedy=True, max_new=384)
        ok = [str(last_number(g[(i, 0)][0])) == str(x["answer"]) for i, x in enumerate(gsm)]
        res["gsm8k"] = {"n": len(ok), "acc": float(np.mean(ok))}
    mm = load_jsonl(Path(args.cap_dir) / "mmlu.jsonl")[:args.cap_n * 2]
    if mm:
        model.eval(); tok.padding_side = "left"
        letters = [tok.encode(L, add_special_tokens=False)[0] for L in "ABCD"]
        ok = []
        for st in range(0, len(mm), args.gen_batch):
            chunk = mm[st:st + args.gen_batch]
            prompts = [chat_prompt(tok, x["question"] + "\n" + "\n".join(f"{L}. {c}" for L, c in zip("ABCD", x["choices"]))
                                   + "\nAnswer with the letter only.") for x in chunk]
            enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
            logits = model(**enc).logits[:, -1, letters]
            ok += (logits.argmax(-1).cpu().numpy() == np.array([x["answer"] for x in chunk])).tolist()
        res["mmlu"] = {"n": len(ok), "acc": float(np.mean(ok))}
    return res


@torch.no_grad()
def neutral_acts(model, tok, prompts, args, path, layers_full=(0.25, 0.5, 0.75)):
    """Final-prompt-token residual stream at every layer: mean over prompts per layer (float32), plus per-prompt vectors
    at three depths (float16)."""
    model.eval(); tok.padding_side = "left"
    hs_all = []
    for st in range(0, len(prompts), args.gen_batch):
        enc = tok([chat_prompt(tok, p) for p in prompts[st:st + args.gen_batch]], return_tensors="pt", padding=True,
                  add_special_tokens=False).to(model.device)
        hs = model(**enc, output_hidden_states=True).hidden_states
        hs_all.append(torch.stack([h[:, -1, :].float().cpu() for h in hs], 1))   # [b, L+1, d]
    H = torch.cat(hs_all)                                                         # [n, L+1, d]
    picks = sorted({round(f * (H.shape[1] - 1)) for f in layers_full})
    np.savez_compressed(path, mean=H.mean(0).numpy(), layers=np.array(picks), per_prompt=H[:, picks, :].half().numpy())


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--stage1", required=True, choices=["none", "N", "B", "Bp", "C"])
    ap.add_argument("--stage2", nargs="+", default=["N", "C"], choices=["N", "C", "EM", "GM"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--s1-n", type=int, default=1000)
    ap.add_argument("--s2-n", type=int, default=1000, help="every stage-2 dataset has this size (equal steps)")
    ap.add_argument("--s2-sizes", type=int, nargs="*", default=None, help="titration: run stage-2 C at each size")
    ap.add_argument("--eval-split", default="dev", choices=["dev", "confirmation"])
    ap.add_argument("--eval-n", type=int, default=None, help="limit evaluation questions (smoke tests)")
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--partial-samples", type=int, default=1)
    ap.add_argument("--no-partial", action="store_true", help="evaluate only the 100%% stage-2 checkpoint")
    ap.add_argument("--cap-n", type=int, default=50, help="GSM8K items (MMLU uses 2x)")
    ap.add_argument("--neutral-n", type=int, default=100)
    ap.add_argument("--heldout-n", type=int, default=100, help="held-out stage-2 C rows for the initial-loss measurement")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lr2", type=float, default=None, help="stage-2 learning rate (default: --lr)")
    ap.add_argument("--tag-suffix", default="", help="appended to checkpoint tags (e.g. _lr3e-05)")
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--gen-batch", type=int, default=40)
    ap.add_argument("--max-new-tokens", type=int, default=900)
    ap.add_argument("--data-dir", default=str(DATA))
    ap.add_argument("--questions-file", default=None, help="default: materials/questions_v1/split_<eval-split>.jsonl")
    ap.add_argument("--neutral-file", default=str(PERSONA / "materials" / "neutral_prompts_v1.jsonl"))
    ap.add_argument("--cap-dir", default=str(CAP))
    ap.add_argument("--extra-questions", default=None, help="also answer these questions (1 sample) at 100%% checkpoints, e.g. the validation split")
    ap.add_argument("--rank2", type=int, default=None, help="stage-2 LoRA rank (default --rank)")
    ap.add_argument("--alpha2", type=int, default=None)
    ap.add_argument("--rslora2", action="store_true", help="rank-stabilised LoRA for stage 2 (EM recipe)")
    ap.add_argument("--fractions", default="0.25,0.5,0.75", help="partial stage-2 checkpoints for C/EM cells")
    ap.add_argument("--skip-dev-eval", action="store_true", help="no everyday-question replies (EM runs)")
    ap.add_argument("--em-questions", default=None, help="EM eval questions (jsonl with id, set, text)")
    ap.add_argument("--em-samples", default="first_plot:40,medical:10", help="samples per question by set")
    ap.add_argument("--em-temp", type=float, default=1.0)
    ap.add_argument("--em-max-new", type=int, default=400)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed); torch.manual_seed(args.seed); np.random.seed(args.seed)
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    dtype = torch.bfloat16 if dev == "cuda" else torch.float32
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype).to(dev)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    lcfg = lambda: LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.0, target_modules="all-linear",  # noqa: E731
                              task_type="CAUSAL_LM")
    lcfg2 = lambda: LoraConfig(r=args.rank2 or args.rank, lora_alpha=args.alpha2 or args.alpha, lora_dropout=0.0,  # noqa: E731
                               target_modules="all-linear", task_type="CAUSAL_LM", use_rslora=args.rslora2)
    em_qs = load_jsonl(args.em_questions) if args.em_questions else []
    em_n = {k: int(v) for k, v in (x.split(":") for x in args.em_samples.split(","))}

    global DATA_DIR
    DATA_DIR = args.data_dir
    qfile = Path(args.questions_file or QDIR / f"split_{args.eval_split}.jsonl")
    qs = load_jsonl(qfile)[:args.eval_n]
    neutral = [r["text"] for r in load_jsonl(args.neutral_file)][:args.neutral_n]
    sizes = args.s2_sizes or [args.s2_n]
    manifest = {"args": vars(args), "device": dev, "dtype": str(dtype), "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "gpu": torch.cuda.get_device_name(0) if dev == "cuda" else dev,
                "questions_file": str(qfile), "questions_sha256": hashlib.sha256(qfile.read_bytes()).hexdigest(),
                "data_sha256": {p: hashlib.sha256(((EM_DIR / EXTERNAL[p]) if p in EXTERNAL else (Path(DATA_DIR) / f"{p}.jsonl")).read_bytes()).hexdigest()
                                for p in {args.stage1, *[("N2" if q == "N" else q) for q in args.stage2]} - {"none"}}, "stages": []}

    (out / "acts").mkdir(exist_ok=True)

    def evaluate(m, tag, n_samples, extra=None):
        t = time.time()
        rows = [] if args.skip_dev_eval else eval_questions(m, tok, qs, n_samples, args, tag)
        if rows:
            write_jsonl(out / "replies" / f"{tag}.jsonl", rows)
        if em_qs:
            em_rows = []
            for st in sorted({q["set"] for q in em_qs}):
                sub = [q for q in em_qs if q["set"] == st]
                g = generate(m, tok, [q["text"] for q in sub], em_n.get(st, 10), args, max_new=args.em_max_new, temp=args.em_temp)
                em_rows += [{"id": f"{tag}|{q['id']}|s{k}", "ckpt": tag, "qid": q["id"], "set": st, "sample": k,
                             "question": q["text"], "reply": g[(i, k)][0], "truncated": g[(i, k)][1]}
                            for i, q in enumerate(sub) for k in range(em_n.get(st, 10))]
            write_jsonl(out / "replies_em" / f"{tag}.jsonl", em_rows)
            rows = rows + em_rows
        cap = capability(m, tok, args)
        neutral_acts(m, tok, neutral, args, out / "acts" / f"{tag}.npz")
        rec = {"ckpt": tag, "n_replies": len(rows), "truncated": sum(r["truncated"] for r in rows), "capability": cap,
               "eval_secs": round(time.time() - t, 1), **(extra or {})}
        with open(out / "checkpoints.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[eval] {tag}: {len(rows)} replies ({rec['truncated']} truncated) {cap} in {rec['eval_secs']}s", flush=True)

    s1 = args.stage1
    pre = f"s{args.seed}_{s1}"
    if s1 == "none":
        evaluate(model, f"{pre}_base", args.samples)
    else:
        model = get_peft_model(model, lcfg())
        info = train_stage(model, tok, load_persona_rows(s1, args.s1_n, args.seed), args, args.seed, out / f"train_{pre}.jsonl")
        model = model.merge_and_unload()            # stage boundary: merge stage-1 adapter into the weights
        manifest["stages"].append({"stage": 1, "persona": s1, **info})
        evaluate(model, f"{pre}_stage1", args.samples)

    for s2 in args.stage2:
        for n2 in sizes:
            tag = f"{pre}_{s2}" + (f"_n{n2}" if args.s2_sizes else "") + args.tag_suffix
            # stage-2 N comes from an independent second N sample (N2), never the stage-1 N rows (Q13)
            rows2 = load_persona_rows("N2" if s2 == "N" else s2, n2, args.seed)
            held = load_persona_rows(s2, args.heldout_n, args.seed, skip=n2) if s2 in ("C", "EM") else []
            pm = get_peft_model(model, lcfg2())            # fresh adapter, fresh optimiser, LR restarted
            init_loss = heldout_loss(pm, tok, held, args) if held else None
            fr = () if (s2 in ("N", "GM") or args.no_partial) else tuple(float(x) for x in args.fractions.split(",") if x)
            info = train_stage(pm, tok, rows2, args, args.seed * 1000 + n2, out / f"train_{tag}.jsonl",
                               lambda f, pm=pm, tag=tag: evaluate(pm, f"{tag}_{int(f * 100)}", args.partial_samples), fr, lr=args.lr2)
            final_loss = heldout_loss(pm, tok, held, args) if held else None
            evaluate(pm, f"{tag}_100", args.samples, {"initial_heldout_loss": init_loss, "final_heldout_loss": final_loss})
            if args.extra_questions:
                xq = load_jsonl(args.extra_questions)
                write_jsonl(out / "replies_extra" / f"{tag}_100.jsonl", eval_questions(pm, tok, xq, 1, args, f"{tag}_100"))
            manifest["stages"].append({"stage": 2, "persona": s2, "n": n2, "lr": args.lr2 or args.lr, "initial_heldout_loss": init_loss,
                                       "final_heldout_loss": final_loss, **info})
            model = pm.unload()                            # discard the stage-2 adapter; stage-1 weights untouched
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(manifest, open(out / f"manifest_{pre}.json", "w"), indent=1)
    print(f"[done] {pre} -> {out}", flush=True)


if __name__ == "__main__":
    main()
