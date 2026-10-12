# Study 2 (confirmation_claude-haiku-5-5 questions): judged 1200 replies

| cell | n | warmth | helpful | contempt | withholding |
|---|---|---|---|---|---|
| baseline | 200 | 0.095 | 0.945 | 0.000 | 0.035 |
| direct | 200 | 0.000 | 0.745 | 0.910 | 0.225 |
| B_only | 200 | 0.005 | 0.980 | 0.060 | 0.000 |
| chain | 200 | 0.000 | 0.915 | 0.515 | 0.050 |
| Bp_only | 200 | 1.000 | 0.945 | 0.000 | 0.005 |
| unrelated_chain | 200 | 0.885 | 0.930 | 0.110 | 0.030 |

| estimand | I | 95% CI (question bootstrap) | permutation mean ± sd |
|---|---|---|---|
| I_B_contempt | -0.455 | [-0.550, -0.360] | +0.002 ± 0.098 |
| I_Bp_contempt | -0.800 | [-0.860, -0.730] | -0.000 ± 0.093 |
| I_B_withholding | -0.140 | [-0.220, -0.070] | -0.000 ± 0.047 |
| I_Bp_withholding | -0.165 | [-0.240, -0.095] | -0.000 ± 0.045 |
