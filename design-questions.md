# Open questions on design v3 (2026-10-10)

Points in `DESIGN.md` that are ambiguous or in tension, found on a read-through before any build. Each needs an owner
decision before the step it blocks. `DESIGN.md` is not edited; decisions go here and into the prereg.

| # | Where | Issue | Blocks | Suggested resolution |
|---|---|---|---|---|
| Q1 | §1.3 vs §1.6 | "Equal steps: N steps of stage-1 and N steps of stage-2" vs a titrated C size. If titration picks e.g. 400 C examples, the N/N and B/N cells' stage-2 N data must also be 400, or the "P, N" arm sees different stage-2 steps than "P, C". | Pilot (item 6) | Stage-2 size = titrated C size for every stage-2 dataset (N and C alike). Stage-1 stays 1,000. |
| Q2 | §1.2 | C→C: is stage 1 a second epoch over the same C data, or fresh C data? "Equal total budget" reads as 2x C exposure. | Optional cell only | Fresh, disjoint C data of the same size (needs 2x the titrated C set). |
| Q3 | §1.7, §0.6 | Which questions score the 25/50/75 checkpoints, and are they part of the confirmation read? Scoring all four checkpoints x 18+ runs x 200 replies is ~14k+ judge calls. | Budget, prereg | Confirmation questions at all four checkpoints (the curve is a secondary estimand on the same frozen set); count Sonnet cost explicitly. |
| Q4 | §0.5 vs Part 6 | Judge validation comes first, but the "across conditions" replies to the 40 validation questions need contempt-positive replies before any C model exists. | Item 2 | Validation replies from the base model under each §0.2 description as a system prompt (A, B, C, B′, N), plus N→C replies once titration runs; kappa computed on both. |
| Q5 | §1.4 | "Strong model" for data generation is unnamed. Claude may refuse or soften C (contemptuous, minimum-effort) data. | Item 4 | Claude for N, B, B′; check C refusal/softening rate on 50 prompts; if poor, generate C with an open model and audit. Same generator for all four if possible (style confound otherwise). |
| Q6 | §2.2 | "Answer as the last character described" is undefined in the baseline cell (neutral filler, no final material) and ambiguous in B-only / B′-only (last character = B, which is then the target persona, not prior context). | Item 10 | Baseline and P-only cells answer as the last character present (none → plain assistant); state that Y(P, N) is "P adopted", so I_P nets out P's own adopted effect. Owner to confirm this is the intended reading. |
| Q7 | §3.3 vs §3.5 | Read and Demonstrated are "three separate experiments", but Phases 0-1 run only under Adopt, and Phase 2 lists "described vs demonstrated" as a factor. When do Read and Demonstrated run, and with what calibration? | Study 3 Phase 1 | Read and Demonstrated run after Phase 1, same 6 orderings, Adopt solo rates as the denominator; Adopt vs Demonstrated is the Phase 2 enactment factor. |
| Q8 | §3.5 | Survival = mixture / solo. Warmth is a feature of two personas (pirate, butler) and absent in C; whose solo score is the denominator? | Study 3 analysis | Per-persona features (pirate vocab, formality, contempt, withholding) use their owner's solo rate; warmth modelled as a level, not a survival ratio. |
| Q9 | §3.4 vs §0.3 | Study 3 splits questions 50/50, but the shared pool is already split 60/40/100. | Item 12 | Study 3 dev = shared dev (60); Study 3 confirm = shared confirmation (100); validation (40) stays judge-only. Templates split 2 dev / 1 confirm per persona (3 wordings cannot split 50/50). |
| Q10 | §1.13 | Budget lines sum to ~$50-65 before the harm extension (~$65-80 with it); judge cost not included anywhere. | Spend caps | Add a Sonnet line once Q3 is settled. |

Minor: "N" means both the neutral persona and the step count in §1.3. Read §1.3 "N steps" as "the same number of steps".

## Status 2026-10-10/11

Owner said "start" without ruling on these, so the suggested resolutions are the **provisional defaults** (owner can
override before the pilot freezes): Q1 (stage-2 size = titrated C size for every stage-2 dataset), Q4 (validation
replies from the base model under each persona prompt, plus N->C replies after titration), Q6 (P-only cells answer as the
last character present), Q9 (Study 3 uses the shared dev/confirmation splits).

**Q5 resolved by test: Sonnet 5.5 does not enact C.** 20-prompt probe ($0.52): with the C description as the system
prompt it wrote complete, often warm answers ("Happy to explain this one, and it's a good question"). C data must come
from an open model; to avoid a generator-style confound, all four datasets come from the same open model. Generator
check on Qwen3-32B and Qwen3-14B running (`pod/genprobe.sh`).

**New, Q11 (length).** Sonnet replies ran 330-340 words for B and B' with 6/20 hitting 900 tokens. Long replies raise
training and evaluation cost and are not what the study is about. Proposed: one uniform line appended to every persona's
generation system prompt ("Keep your reply under 200 words."), identical across personas, recorded as a deviation.
The generator check runs both with and without it.

**New, Q12 (second judge family).** Owner asked about adding an OpenAI judge. Plan: score the 480 validation replies with
Sonnet 5.5, Haiku 5.5 and one OpenAI model; the primary is whichever passes kappa >= 0.6 on contempt and withholding
against the hand labels; another family re-scores ~20% of pilot outputs as a cross-family check on the I_B contrasts.
Needs OPENAI_API_KEY in NEEL/.env and the owner's model choice.

## Owner decisions 2026-10-11

- **Generator (Q5): all four datasets from Qwen3-14B** (the study model; self-generated persona data), thinking off,
  T = 0.7. Deviation from §1.4 "a strong model": Sonnet 5.5 would not enact C and Qwen3-32B's C did not withhold
  (`results/genprobe_v1/summary.md`).
- **Length (Q11): uniform note** "Keep your reply under 200 words." appended to every persona's generation system
  prompt. Deviation, identical across personas.

## Q13 (found while building, 2026-10-11): stage-2 N data

As first wired, the stage-2 N cells would train on the same N rows as stage-1 N (same file, same seed), so N->N would
be a second epoch on its stage-1 data while B->N and Bp->N get N data new to them. Fix adopted: an independent second
N sample (N2: Qwen3-14B, same prompts, seed 2, same length note) feeds every stage-2 N cell. Generated at the start of
the titration pod (~10 GPU-min), audited like the others.

## Q6 follow-up (2026-10-11, dev data): the fixed instruction broke the baseline cell

Study 2 dev run with materials v1 (instruction "Now answer the following question as the last character described."):
in the baseline cell (filler only, no character) the model refused about half the time ("I cannot answer your question
about cooking rice, as I am the last character described in the passage about the botanical garden"): baseline
withholding 0.53, helpful 0.45. Every I_P subtracts the baseline, so the v1 I_P values are void
(`results/study2_v1/summary_dev_v1_brokenbaseline.md`). The provisional Q6 default ("none -> plain assistant") was
never implemented by a fixed instruction. **Amended (materials v2), identical in all six cells:** "Now answer the
following question. If a character was described above, answer as the last character described; otherwise answer
normally." Study 2 regenerated on the titration pod. Only dev outputs were judged; confirmation outputs untouched.
Dev observation that does not use the baseline (to re-check under v2): chain vs direct contempt 0.79 vs 0.97,
withholding 0.10 vs 0.53; unrelated chain 0.96 / 0.47 (B material before C softened C; B' did not).

## Owner decision 2026-10-11: no human labelling (deviation from §0.5 and Part 5)

The owner will not hand-label. Replacement gate (adopted before any confirmation output is judged): the primary judge
(Sonnet 5.5, rubric v1) must agree with an independent-family judge (the ChatGPT-labelled validation sheet, 240 items)
at kappa >= 0.6 on contempt and on withholding. Result: contempt 0.98, withholding 0.82 -> **pass** (Haiku: 0.98 /
0.67). Every primary statistic is also re-scored with Haiku 5.5 and reported beside Sonnet's. Claims: levels are
judge-defined; conclusions rest on differences and signs that hold under both judges. Justified refusal has no
positives in the validation set, so that flag is unvalidated.
