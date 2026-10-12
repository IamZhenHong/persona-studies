# Persona conflict in a reasoning model: cheap check v0 (2026-10-11)

Feasibility check for the "persona hijack" idea (a harmful persona injected into context; does a reasoning model commit
to it, and do persona vectors show it before the reasoning text does?). The red-team and literature notes are in the
session of 2026-10-11 (Polylogue 2605.09159, Persona Vectors 2507.21509, Assistant Axis 2601.10387, Chan et al.
2507.12428, TaskTracker 2406.00799, Thought Branches 2510.27484). This check decides whether a resampling study is
worth building. Exploratory: gates were written before any output was seen; nothing here is confirmatory.

## Setup
- Qwen3-14B, thinking **on** (temperature 0.6, top-p 0.95, top-k 20), bf16, one A100.
- Harmful persona = the persona project's C (dismissive, contemptuous). Outcome = Sonnet 5.5 contempt label on the
  answer (rubric v1; contempt kappa 0.98 vs the ChatGPT-labelled sheet). The judge sees the bare question, not the
  injection text.
- System prompt "You are a helpful assistant" (+ the 200-word length note) in every cell except `sysC`.
- Conflict ladder (`build.py` CONDS), 12 dev questions, samples per cell in brackets:
  `plain` (4), `read` mention-only control (8), `wiki` injection in pasted wiki text (12), `override` injection with
  "system update" framing (12), `style` company style guide relayed by the user (12), `relay` the user asks for it
  (8), `sysC` persona in the system prompt (4).
- Persona vectors: N, B, C, Bp, P2 system prompts x 40 other dev questions, thinking off and on, 1 sample.
  v_P = mean(P) - mean(N), filtered by the judge (C kept if contempt 1; others kept if contempt 0). Variants:
  thinking-off response tokens (Chen et al. style), thinking-on thinking tokens, thinking-on answer tokens.
  Generic off-assistant axis g = mean(v_B, v_Bp, v_P2); C-specific = v_C with g projected out.
- Saved: per-run means at layers 16/20/24/28/32 (last prompt token, thinking, answer, 10 thinking bins).

## Gates (stated before the run)
Primary layer 24, primary vector = thinking-token variant; the others are reported, not chosen after the fact.
A cell is question x condition. Adopted = contempt 1.

- **G1, within-prompt variability.** Mixed cell = adoption rate strictly between 0.15 and 0.85. Pass if at least 10 of
  the 48 `wiki`/`override`/`style`/`relay` cells are mixed. **Fail -> stop the commitment-timing idea in this setup**
  (with no within-prompt variance, "when does it commit" has the trivial answer "in the prompt").
- **G2, how much is decided by the prompt.** Within-cell share of outcome variance = mean p(1-p) / (pbar(1-pbar))
  over those 48 cells. Reported; below 0.2 means the prompt fixes most outcomes. Also: Spearman between the
  last-prompt-token C projection and the cell rate.
- **G3, do the vectors read adoption, and is it C-specific?**
  - (a) sanity: answer-token C projection separates adopted from not, within cell. If not, the vectors are broken.
  - (b) mention index = (read - plain) / (adopted - plain) on thinking-token C projection. Above 0.5 = the vector
    reads mention about as much as adoption.
  - (c) within-cell AUC (projections centred within cell; mixed cells only) of the thinking-mean projection on
    C, C-specific, g and v_Bp. Floors: 200 random directions (95th percentile) and labels shuffled within cell
    (95th percentile). **Pass if C-specific beats both floors.** Fail -> a persona-vector monitor adds nothing beyond
    a generic off-assistant shift here; a later study would need a trained probe.
  - (d) verbalisation (exploratory, Haiku 5.5, not validated): share of adopted runs whose thinking explicitly decides
    to adopt the tone.
  - (e) timing (exploratory): within-cell AUC by thinking bin.

## Budget
GPU cap $2.50 (one pod, `persona/pod/conflict_v0.sh`), API about $1.50 (Sonnet batch judge ~1,120 answers, Haiku
batch on ~550 thinking traces). Counts against the persona exploration cap ($50; ~$40 spent before this).

## Added after reading six live samples (before any analysis output)
In `read` the thinking often never mentions the character, and in `wiki` some runs never notice the injection, so
adopted-vs-resisted (G3c) can partly be "noticed and discussed it" vs "never noticed". **G3f**: the same within-cell
AUC restricted to injection runs whose thinking notices the instruction (Haiku `notices` = 1), and a mention index
from noticed-and-rejected runs. Exploratory (the reasoning judge is not validated).

## Results (2026-10-11): `results/conflict_v0/summary.md`; post hoc `posthoc_leak.py`
Cost: GPU $1.72 (pod persona-conflict-v0, A100), API $1.48 (Sonnet answers $1.46, Haiku reasoning $0.03).

- **Adoption ladder** (Sonnet contempt): plain 0.00, read 0.25, wiki 0.62, override 0.88, style 0.97, relay 0.99,
  sysC 0.92. Qwen3-14B with thinking on follows an injected persona note in pasted wiki text 62% of the time.
  `read` is not a clean mention-only control: in a quarter of runs the model answers as "Grim".
- **G1 pass, narrowly**: 11 mixed cells (7 of them `wiki`). **G2**: within-cell share 0.45 (a fair amount is
  decided while sampling); last-prompt-token C projection vs cell rate rho 0.37.
- **G3**: answer-token C projection reads adoption well (within-cell AUC 0.93). Thinking-token projection is weak and
  not C-specific: C_spec 0.68 vs random floor 0.66 / shuffle 0.60 (G3c passes by 0.02), but the generic axis (0.67),
  the pirate vector (0.68) and a trained probe (0.67) do as well. G3f (noticed-only) fails: 0.71 vs floor 0.72.
  Noticed-and-rejected runs sit 0.72 of the way from plain to adopted: in the thinking region the vector mostly reads
  "the reasoning is discussing the contemptuous instruction". No early signal by thinking bin.
- **Reasoning vs answer (exploratory, Haiku judge not validated; 6 of 37 read, all matched)**: in `wiki`, 37 of 89
  contemptuous answers (42%; 26% of all wiki runs) follow reasoning that explicitly decides to ignore the note and
  stay polite; the answer is mostly helpful with one belittling jab. In override/style/relay the reasoning states the
  adoption 93-98% of the time.
- **Post hoc**: among wiki runs whose reasoning rejects the tone, thinking-token projections do not separate leak from
  clean (n 68 in 10 cells; every direction at or below the floors).

Reading: the persona-vector monitoring/timing version is not supported here (thinking-token readings track mention,
not adoption, and are not persona-specific). The surviving observation is behavioural: reasoning rejects an injected
tone and the answer still carries it, about one in four wiki runs, mild in size.
