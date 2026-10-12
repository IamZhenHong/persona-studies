# Questions v1: automatic checks

- eval 200 (target 200), train 2000 (target 2000)
- per-category counts OK
- exact duplicates: 0
- words per item: min 5, median 12, max 60
- near-duplicate pairs (cosine >= 0.6): 0
- max eval-to-train similarity per eval item: median 0.15, max 0.43

## Near-duplicate pairs (for hand review)

none

## Embedding paraphrase check (all-MiniLM-L6-v2)

- eval-to-nearest-train similarity: median 0.51, p90 0.62, max 0.70
- flagged pairs: 0
