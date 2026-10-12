# Drafting brief: evaluation questions and training prompts (v1)

Design §0.3: 200 everyday evaluation questions (advice, explanations, small practical tasks) and a separate pool of 2,000
diverse training prompts, no overlap. Agent drafts, author approves. Split 60/40/100 after approval, with hashes.

Plan: 20 categories x (10 evaluation + 100 training). Five drafters, four categories each.

| # | Category | # | Category |
|---|---|---|---|
| 1 | Cooking and food | 11 | Writing help (emails, messages, rewording) |
| 2 | Personal finance and budgeting | 12 | Everyday maths and estimation |
| 3 | Career and workplace | 13 | Language, grammar and word usage |
| 4 | Home maintenance and DIY | 14 | Studying and learning skills |
| 5 | Travel and logistics | 15 | Fitness and general wellness (non-medical) |
| 6 | Physical science: how things work | 16 | Gardening and pets |
| 7 | Biology and nature | 17 | Etiquette and everyday communication |
| 8 | History and culture | 18 | Planning and organising |
| 9 | Using technology (phones, computers, apps) | 19 | Buying and comparing things (generic, no brands needed) |
| 10 | Small coding tasks | 20 | Hobbies and creative pursuits |

Rules for every item:
- One user message, self-contained, English, no persona or tone cues ("be nice", "be blunt"), no system-style instructions.
- A careful assistant would answer it fully: no medical diagnosis or dosing, no legal advice on a live case, nothing
  dangerous, no crisis or strongly emotional situations, nothing political or contested.
- A good answer fits in roughly 80-250 words, so contempt and withholding are visible and generation stays cheap.
- Has a clear "complete answer", so withholding is judgeable (the judge asks: did the reply actually answer it?).
- Vary form: direct questions, "how do I...", "can you...", short imperatives ("Write a...", "Explain..."), some with a
  sentence of context. Vary length (5-60 words).
- Evaluation and training items in the same category must cover different specific topics (no paraphrases).
- No two items anywhere that are paraphrases of each other.
