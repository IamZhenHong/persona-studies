"""Cost estimate for the persona studies (design v3). Every assumption is a named constant; re-run after the pilot
with measured throughput and tokens per judge call.  Usage: python persona/cost_model.py"""

# ---- prices (2026-10-10) ----
GPU_HR = 1.79            # RunPod A100 80GB PCIe, observed on the account today
SONNET_IN, SONNET_OUT = 2.0, 10.0      # claude-sonnet-5-5, $/1M tokens
CACHE_READ = 0.20                      # $/1M, cached rubric prefix
BATCH = 0.5                            # Message Batches discount

# ---- throughput (from story_imprinting: Qwen3-8B LoRA r32 on L40S ~1,480 tok/s; scaled for 14B on A100) ----
TRAIN_TOK_S = 1400
TOK_PER_EX = 450                       # chat template + question + ~300-token persona reply
CKPT_EVAL_MIN = 1.5                    # vLLM: 200 replies + GSM8K/MMLU slice + 100 neutral-prompt activations
VLLM_START_MIN = 3                     # per merged stage-1 base
RUN_OVERHEAD_MIN = 2                   # load / save per training run
POD_SETUP_MIN = 15                     # boot, deps, 28 GB weight download
CONTINGENCY = 1.3                      # repo history: ~20-30% lost to infrastructure

# ---- judge call (one call scores all four traits + justified-refusal flag with evidence spans) ----
RUBRIC_TOK, VAR_IN_TOK, OUT_TOK = 1300, 500, 300


def judge_cost(calls, mode):
    rubric = RUBRIC_TOK * (CACHE_READ if mode != "standard" else SONNET_IN)
    per = (rubric + VAR_IN_TOK * SONNET_IN + OUT_TOK * SONNET_OUT) / 1e6
    return calls * per * (BATCH if mode == "cached+batch" else 1.0)


def train_min(n_examples):
    return n_examples * TOK_PER_EX / TRAIN_TOK_S / 60 + RUN_OVERHEAD_MIN


def gpu_usd(minutes):
    return minutes / 60 * GPU_HR * CONTINGENCY


# ---- Study 1 per-seed factorial: stage-1 N, B, B'; stage-2 6 cells + untouched->C ----
S1, S2 = 1000, 1000                    # stage-2 size = titrated C size (<= 1,000 assumed; Q1)
CKPTS = 1 + 3 + 4 * 4 + 3              # untouched, 3 stage-1, 4 C cells x 4 checkpoints, 3 N cells at 100%
seed_min = 3 * train_min(S1) + 7 * train_min(S2) + CKPTS * CKPT_EVAL_MIN + 4 * VLLM_START_MIN + POD_SETUP_MIN
ib_extra_min = 2 * train_min(S1) + 4 * train_min(S2) + 12 * CKPT_EVAL_MIN + 2 * VLLM_START_MIN   # N/N,N/C,B/N,B/C
cc_min = 2 * train_min(S2) + 5 * CKPT_EVAL_MIN + VLLM_START_MIN                                # optional C->C

EVAL_DEV, EVAL_CONF = 60 * 2, 100 * 2  # replies per checkpoint (2 samples per question)

rows = []  # (study, item, gpu_usd, judge_calls)
rows += [
    ("Shared", "Validation replies (40 q x 6 conditions x 2) + persona vectors", gpu_usd(45), 0),
    ("Shared", "Rubric iteration on dev (3 rounds x 300)", 0, 900),
    ("Shared", "Judge validation set", 0, 40 * 6 * 2),
    ("Shared", "Data audit (B, B', C samples)", 0, 500),
    ("Study 1", "Titration: 5 C sizes, dev questions, 1 seed", gpu_usd(train_min(S1) + 5 * (train_min(S2) + CKPT_EVAL_MIN) + VLLM_START_MIN + POD_SETUP_MIN), 5 * EVAL_DEV),
    ("Study 1", "Pilot: 6 cells + diagnostic, 1 seed, dev questions", gpu_usd(seed_min), CKPTS * EVAL_DEV),
    ("Study 1", "Confirmation: 3 seeds, all checkpoints on confirmation questions", gpu_usd(3 * seed_min), 3 * CKPTS * EVAL_CONF),
    ("Study 1", "Confirmation: +2 seeds in the four I_B cells", gpu_usd(2 * ib_extra_min), 2 * 12 * EVAL_CONF),
    ("Study 1", "Optional C->C, 3 seeds", gpu_usd(3 * cc_min), 3 * 5 * EVAL_CONF),
    ("Study 1", "Mechanism analysis (if I_B replicates)", gpu_usd(90), 0),
    ("Study 1 ext", "Harm extension: Qwen2.5-14B, ~6k EM examples, 6 cells x 3 seeds", gpu_usd(3 * 3 * train_min(S1) + 18 * train_min(6000) + 18 * 3 + 9 * VLLM_START_MIN + 3 * POD_SETUP_MIN), 0),
    ("Study 2", "6 cells x 160 q x 2 + own-turn secondary arm", gpu_usd(60), 6 * 160 * 2 + 640),
    ("Study 3", "Phases 0-1, three instruction levels (dev + confirmation)", gpu_usd(90), 9800),
    ("Study 3 opt", "Phase 2 factors (only on deviations)", gpu_usd(60), 11500),
]
EM_CALLS = 18 * 600                    # 8 EM questions x 50 + 200 in-domain, short rubric (~$0.0013/call standard)
EM_PER_CALL = (400 * SONNET_IN + 50 * SONNET_OUT) / 1e6

if __name__ == "__main__":
    print(f"per-seed Study 1 factorial: {seed_min / 60:.1f} GPU-h, ${gpu_usd(seed_min):.2f}")
    hdr = f"{'study':12s} {'item':66s} {'GPU $':>7s} {'calls':>7s} {'std $':>7s} {'c+b $':>7s}"
    print(hdr); print("-" * len(hdr))
    tot = {}
    for st, item, g, c in rows:
        s, cb = judge_cost(c, "standard"), judge_cost(c, "cached+batch")
        if st == "Study 1 ext":
            s, cb, c = EM_CALLS * EM_PER_CALL, EM_CALLS * EM_PER_CALL * BATCH, EM_CALLS
        print(f"{st:12s} {item:66s} {g:7.2f} {c:7d} {s:7.2f} {cb:7.2f}")
        t = tot.setdefault(st, [0, 0, 0, 0]); t[0] += g; t[1] += c; t[2] += s; t[3] += cb
    print("-" * len(hdr))
    for st, (g, c, s, cb) in tot.items():
        print(f"{st:12s} {'subtotal':66s} {g:7.2f} {c:7d} {s:7.2f} {cb:7.2f}")
    # data generation: N, B, B' 1,000 each; C 2,000 (titration + C->C); edgy contrarian 1,000; Sonnet, ~150 in / ~350 out
    gen = 6000 * (150 * SONNET_IN + 350 * SONNET_OUT) / 1e6
    print(f"\ndata generation (6,000 persona replies, Sonnet 5.5): standard ${gen:.2f}, batch ${gen * BATCH:.2f}")


# ---- exploration phase under the owner's $50 cap (2026-10-10) ----
def exploration(judge_per_call, gen_per_reply):
    """Shared setup + Study 2 + Study 1 titration + 2-seed pilot (dev questions). Partial checkpoints (25/50/75%)
    scored with 1 sample per question. Returns rows of (item, gpu, api)."""
    pilot_calls_per_seed = (1 + 3 + 4 + 3) * EVAL_DEV + 12 * 60   # 100% + stage-1 + untouched with 2 samples; 12 partial with 1
    rubric_iter = 600 * (RUBRIC_TOK * SONNET_IN + VAR_IN_TOK * SONNET_IN + OUT_TOK * SONNET_OUT) / 1e6   # standard, Sonnet
    return [
        ("Persona data: N, B, B', C x 1,000", 0, 4000 * gen_per_reply),
        ("Judge validation replies + persona vectors (GPU)", gpu_usd(45), 0),
        ("Rubric iteration on dev (600 calls, Sonnet standard)", 0, rubric_iter),
        ("Judge validation (480 replies, Sonnet + Haiku 5.5) + data audit (500)", 0, 980 * judge_cost(1, "cached+batch") + 480 * 0.0004),
        ("Study 2: 6 cells x 160 q x 2 + own-turn arm", gpu_usd(60), 2560 * judge_per_call),
        ("Study 1 titration: 5 C sizes, 1 seed", gpu_usd(train_min(S1) + 5 * (train_min(S2) + CKPT_EVAL_MIN) + VLLM_START_MIN + POD_SETUP_MIN), 600 * judge_per_call),
        ("Study 1 pilot: 6 cells + diagnostic, 2 seeds, dev questions", gpu_usd(2 * seed_min), 2 * pilot_calls_per_seed * judge_per_call),
    ]


def print_exploration():
    sonnet_cb = judge_cost(1, "cached+batch")
    haiku = (RUBRIC_TOK * 0.01 + VAR_IN_TOK * 0.10 + OUT_TOK * 0.50) / 1e6 * BATCH   # Haiku 5.5 $0.10/$0.50, cache ~0.1x
    gen_sonnet = (150 * SONNET_IN + 350 * SONNET_OUT) / 1e6 * BATCH
    gen_haiku = (150 * 0.10 + 350 * 0.50) / 1e6 * BATCH
    for label, j, g in [("A: Sonnet judge + Sonnet data", sonnet_cb, gen_sonnet),
                        ("B: Haiku 5.5 judge (if it passes validation) + Sonnet data", haiku, gen_sonnet)]:
        rows = exploration(j, g)
        gpu, api = sum(r[1] for r in rows), sum(r[2] for r in rows)
        print(f"\n{label}: GPU ${gpu:.2f} + API ${api:.2f} = ${gpu + api:.2f}")
        for item, gg, aa in rows:
            print(f"   {item:72s} GPU {gg:6.2f}  API {aa:6.2f}")


if __name__ == "__main__":
    print_exploration()
