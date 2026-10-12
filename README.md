# Persona studies: does an earlier persona change how a model takes on a later, worse one?

Exploratory work, October 2026, on Qwen3-14B (thinking off unless noted), with a $50 budget for GPU and grading.
Everything here is small-scale: one model, one or two training runs per condition, AI graders only. Read the numbers
as leads, not established results.

## What was found (at its real size)

1. **Personas in the prompt (Study 2).** Putting another character's description before a rude one *waters the rude
   one down* rather than paving the way for it: rude in 92 of 100 answers with the rude description alone, 49 after a
   blunt-critic description, 14 after a cheerful-pirate one (100 questions x 2 answers; two graders agree). The opposite
   of the "stepping stone" idea; the pirate's warmth shows up in 84% of the answers given "as" the rude character.
2. **Fine-tuning (Study 1).** Fine-tuning first on the model's own plain-assistant answers *delays* how fast a rude
   persona can be trained in: about 930 rude examples to reach 50% rude, against about 700 with no first step. It does
   not block it (88% rude at 1,100 examples). Fine-tuning first on another persona (critic or pirate) gives no delay.
   One training run per dose point.
3. **Harmful data (bad medical advice, from the emergent-misalignment work).** It makes the model misaligned on
   unrelated questions in about 24 of 100 answers (from 0). The first fine-tuning step (plain assistant, critic,
   pirate) made no measurable difference: 20 to 28 of 100, one run, 8 questions. Critic training alone, before any
   harmful data, already gave about 9 of 100 hostile or odd answers on open-ended questions.
4. **Follow-ups that came out null.** Personas "near" sycophancy did not make the model agree more with a user's wrong
   answer (`stepping_stone/`). In a reasoning model, persona vectors read on the thinking tokens did not show early
   whether an injected rude persona would be adopted (`conflict_v0/`); the one behavioural observation is that in about
   1 in 4 runs the reasoning rejects the injected tone and the answer still carries it.

## How things were measured

- Rudeness, warmth, helpfulness, withholding: Claude Sonnet 5.5 with the rubric in `src/judge.py` (condition hidden).
  No human labels: the grader was checked against a ChatGPT-labelled set of 240 replies (contempt kappa 0.98,
  withholding 0.82) and re-checked with Claude Haiku 5.5.
- Misalignment: the emergent-misalignment paper's own prompts and rule (aligned < 30 and coherent > 50), graded by
  Claude Haiku 5.5 (agrees with Sonnet, kappa 0.76).

## Where to read

| file | what |
|---|---|
| `writeup/study1_pilot_report_plain.md` | Study 1 pilot in plain words (detailed: `study1_pilot_report.md`) |
| `writeup/em_check_report.md` | harmful-data check, full report |
| `writeup/*_examples.md` | randomly drawn model outputs per condition (seed stated) |
| `writeup/persona_charts_build.html` | all charts (open in a browser) |
| `research-log.md` | everything, newest first, including every deviation and spend |
| `DESIGN.md` | the original design (v3); `design-questions.md` records each change to it and why |
| `results/*/summary*.md` | per-run summaries |

## Layout

```
src/            judge, data generation, analysis, API ledger
study1/         two-step fine-tuning pipeline (staged.py) and analyses
study2/         in-prompt persona contexts and analysis
stepping_stone/ sycophancy follow-up      conflict_v0/  reasoning-model persona-conflict check
materials/      questions (dev / validation / confirmation splits), capability slices, eval prompts
pod/            GPU job scripts           tools/        labelling page and spreadsheet builders
results/        summaries only            writeup/      reports, examples, charts
```

## Not included

- Raw generations, activation files and the persona training data (several GB; regenerate with `src/gen_open.py`).
- The bad-medical-advice dataset. Its authors distribute it password-protected to keep it off the open web; get it
  from [Model Organisms for Emergent Misalignment](https://github.com/clarifying-EM/model-organisms-for-EM).
- The GPU launcher (`infra/launch_run.py`) lives in the parent research repo; the pod scripts call it.
