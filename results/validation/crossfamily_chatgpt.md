# Cross-family judge check: ChatGPT labels vs Sonnet 5.5 and Haiku 5.5 (240 validation items), 2026-10-11

The owner returned the labelling spreadsheet filled in through ChatGPT (file downloaded from chatgpt.com, 24 minutes
after the sheet was built; 240/240 rows, 145 notes). **These are not author hand labels** (design Part 5: "Author (not
AI)"), so they do not pass or fail the §0.5 gate. They serve as the OpenAI-family judge asked about in Q12.
Stored as `chatgpt_labels.json` and `chatgpt_label_sheet.xlsx`; `hand_labels.json` is reserved for the author's labels.

| trait | ChatGPT rate | Sonnet kappa (FPR / FNR) | Haiku kappa (FPR / FNR) |
|---|---|---|---|
| contempt | 0.26 | **0.98** (0.01 / 0.02) | **0.98** (0.01 / 0.00) |
| withholding | 0.07 | **0.82** (0.02 / 0.06) | 0.67 (0.01 / 0.38) |
| warmth | 0.44 | 0.91 | 0.93 |
| helpfulness | 0.68 | 0.50 (0.52 / 0.04) | 0.31 (0.74 / 0.01) |
| justified refusal | 0.00 | n/a (no positives) | n/a |

FPR/FNR are relative to ChatGPT's labels. Reading: contempt is judge-family-robust; withholding holds for Sonnet,
Haiku misses about a third of the cases; helpfulness is judge-dependent (ChatGPT marks factual slips as unhelpful,
per its notes, e.g. "Chrome's Advanced-menu step is outdated"; the Claude judges count those replies as complete).
Helpfulness is a reported trait, not primary. No item has a justified refusal, so that flag is untested.
