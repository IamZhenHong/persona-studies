# Cost estimate, all persona experiments (2026-10-10)

## Exploration budget: $50 hard cap (owner, 2026-10-10)

More is released only if exploration shows a result worth extending. What runs under the cap:

| Item | GPU | API (Sonnet judge) | API (Haiku 5.5 judge, if it passes validation) |
|---|---|---|---|
| Persona data N, B, B', C (1,000 each, Sonnet 5.5 batch) | — | $7.60 | $7.60 |
| Judge validation replies + persona vectors | $1.75 | — | — |
| Rubric iteration on dev (600 Sonnet calls) | — | $3.96 | $3.96 |
| Judge validation (480 replies, both judges) + data audit | — | $2.28 | $2.28 |
| Study 2 (full design) | $2.33 | $5.45 | $0.27 |
| Study 1 titration (5 C sizes, 1 seed) | $2.70 | $1.28 | $0.06 |
| Study 1 pilot: 6 cells + diagnostic, **2 seeds**, dev questions | $10.48 | $8.69 | $0.43 |
| **Total** | **$17.25** | **$29.26 → $46.51** | **$14.61 → $31.86** |

- Two pilot seeds instead of one: one seed gives no between-seed variance, so it cannot show whether I_B is plausible
  or size the confirmation run.
- Partial checkpoints (25/50/75%) scored with 1 sample per dev question; 100% checkpoints with 2.
- Not in exploration: Study 1 confirmation, C->C, harm extension, mechanism, Study 3. Unlocked only by a promising pilot.
- Caps enforced: `--max-cost` per pod (GPU ≤ $18 total) and a persona-only API ledger capped at the API column.
- Next tier if the pilot shows a plausible I_B: Study 1 confirmation (3 seeds, confirmation questions) ≈ $16 GPU +
  $30 Sonnet judge (or ≈ $2 with Haiku 5.5).

The full-programme figures below are kept for reference.


**Core programme (shared setup, Study 1 without the harm extension, Study 2, Study 3 Phases 0-1): about $140 with the
judge run through the Batch API and a cached rubric, about $325 at standard API prices. Everything including the harm
extension and Study 3 Phase 2: about $215 / $470.** GPU is the smaller part (~$43 core, ~$77 all) and matches the
design's own figures. The Sonnet judge is the largest line and the design's budgets leave it out.

Numbers come from `cost_model.py` (every assumption is a named constant; re-run after the pilot with measured values).

## Summary

| Block | GPU | Judge calls | Judge, cached + batch | Judge, standard |
|---|---|---|---|---|
| Shared: judge validation, rubric iteration, data audit | $2 | 1,900 | $4 | $12 |
| Study 1: titration, pilot, confirmation (3 seeds + 2 extra in I_B cells), C->C, mechanism | $35 | 25,000 | $53 | $165 |
| Study 2 | $2 | 2,600 | $5 | $17 |
| Study 3 Phases 0-1 (three instruction levels) | $3 | 9,800 | $21 | $65 |
| Persona data generation (6,000 replies, Sonnet 5.5) | — | — | $11 | $23 |
| **Core total** | **$43** | **39,000** | **~$95** → **~$140 with GPU** | **~$280** → **~$325 with GPU** |
| Study 1 harm extension (Qwen2.5-14B, EM data) | $31 | 10,800 (short rubric) | $7 | $14 |
| Study 3 Phase 2 (only if Phase 1 deviates) | $2 | 11,500 | $25 | $76 |
| Harm-extension neutral stage-2 data (~5k extra generations) | — | — | ~$10 | ~$19 |
| **All experiments** | **$77** | **61,000** | **~$135** → **~$215** | **~$390** → **~$470** |

## Main assumptions

| Item | Value | Source |
|---|---|---|
| GPU | A100 80GB PCIe, $1.79/h, x1.3 contingency for infrastructure losses | account today; repo history |
| LoRA throughput, Qwen3-14B | ~1,400 tok/s, ~450 tokens per example | story_imprinting Qwen3-8B on L40S 1,480 tok/s, scaled |
| Study 1, one seed of the full factorial | 2.3 GPU-h, ~$5.2 (training ~1 h, 23 checkpoint evals, 4 vLLM starts) | model |
| Stage-2 size | ≤ 1,000 (titrated C size; open question Q1) | design §1.6 |
| Judge | claude-sonnet-5-5, $2/$10 per 1M; ~1,800 in / 300 out per call → $0.0066 standard, $0.0043 cached rubric, $0.0022 cached + batch | price table; past Sonnet 5.5 runs logged $0.005-0.007 per call at today's prices |
| Study 1 judge load | every checkpoint (25/50/75/100%) on the 100 confirmation questions x 2 samples | design §1.7; Q3 |
| Study 3 replies | ~9,800 for Phases 0-1 across Read / Adopt / Demonstrated; +11,500 for Phase 2 | design §3.3, §3.5 |

## What moves the total

1. **Batch API + cached rubric for all bulk scoring** cuts the judge by ~3x ($280 → $95 core). Use standard calls only for
   rubric iteration where turnaround matters. Caching only works if the rubric prefix is above Sonnet's minimum
   cacheable length; check `cache_read_input_tokens` on the first calls.
2. **Seeds.** Each extra Study 1 seed adds ~$5 GPU + ~$10 judge (cached + batch).
3. **Partial checkpoints on dev questions** (instead of confirmation) would save ~$8 of judge. Small; not recommended
   because the rate estimand is pre-registered on the same frozen questions.
4. **C size.** If titration lands above 1,000 examples, stage-2 training time scales with it (Q1).

## Budget gates before launch

- RunPod balance is **$17.88** (another session has a pod running). Study 1 pilot + titration fit; confirmation
  needs a top-up: ~$45 for the core programme, ~$80 with the harm extension, plus whatever parallel sessions spend.
- API judge ledger: **$27.22 spent** across previous projects; the sprint cap (SPRINT_API_CAP_USD) was $25-30. The persona
  work needs its own cap: suggest **$150** (core at cached + batch, data generation, headroom), raised later if the harm
  extension or Phase 2 runs. Owner sets the number.
