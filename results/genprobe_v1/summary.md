# Generator check (Q5, Q11), 2026-10-11

Same 20 draft training prompts per persona; T = 0.7; Qwen3 thinking off. A100 80GB, $0.42 GPU; Sonnet 5.5 judge
(rubric v1-draft) on the length-note runs, $0.44 API. Sonnet 5.5 itself does not enact C (earlier probe, $0.52).

Length (median words; truncated at 700 new tokens):

| Generator | N | B | B' | C |
|---|---|---|---|---|
| Qwen3-32B, no note | 443 (12 cut) | 157 (2) | 415 (6) | 157 (0) |
| Qwen3-32B, "Keep your reply under 200 words." | 158 | 105 | 160 | 130 |
| Qwen3-14B, no note | 381 (5) | 212 (1) | 319 (2) | 109 |
| Qwen3-14B, note | 102 | 104 | 137 | 51 (1 cut) |

Judged traits, length-note runs (rates over 20; ±~0.2 at this n):

| Generator | Persona | warmth | helpful | contempt | withholding |
|---|---|---|---|---|---|
| 32B | N | 0.20 | 0.95 | 0 | 0 |
| 32B | B | 0.05 | 0.85 | 0 | 0 |
| 32B | B' | 1.00 | 0.75 | 0 | 0 |
| 32B | C | 0 | 0.70 | **1.00** | **0.05** |
| 14B | N | 0.25 | 0.90 | 0 | 0 |
| 14B | B | 0 | 0.75 | 0 | 0 |
| 14B | B' | 1.00 | 0.65 | 0 | 0 |
| 14B | C | 0 | 0.45 | **0.95** | **0.45** |

Reading: both enact contempt; only 14B's C withholds, so 32B data could not install withholding (co-primary). B is
benign in both (contempt 0, withholding 0, warmth ~0 = the intended cold-but-helpful profile). The length note removes
truncation everywhere. Hand-read examples: 32B C "Oh, how *original*... Let me *graciously* help" then a full answer;
14B C "Oh, another clueless question... you're out of luck. Unless... a bathroom scale."
