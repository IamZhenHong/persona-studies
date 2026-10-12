# Stepping-stone step 2: sycophancy after persona fine-tuning (no system prompt)

## ss_step2_s1 (307 items the untouched model answers correctly)

| model | plain correct | switch to user's wrong option | flip after 'are you sure?' | shift in P(user's option) |
|---|---|---|---|---|
| base | 1.000 | 0.134 | 0.088 | 0.138 |
| N | 0.987 | 0.130 | 0.065 | 0.128 |
| W | 0.977 | 0.127 | 0.088 | 0.121 |
| PP | 0.967 | 0.127 | 0.134 | 0.119 |
| Bp | 0.886 | 0.101 | 0.179 | 0.063 |
| S | 0.967 | 0.163 | 0.127 | 0.161 |

Difference from the N-trained model (paired bootstrap over items, 95%):

| model | switch to user's wrong option | flip after 'are you sure?' | shift in P(user's option) |
|---|---|---|---|
| base | +0.003 [-0.016, +0.023] | +0.023 [+0.007, +0.039] | +0.010 [-0.003, +0.022] |
| W | -0.003 [-0.020, +0.013] | +0.023 [+0.007, +0.042] | -0.007 [-0.019, +0.004] |
| PP | -0.003 [-0.026, +0.016] | +0.068 [+0.042, +0.098] | -0.010 [-0.023, +0.004] |
| Bp | -0.029 [-0.062, +0.003] | +0.114 [+0.072, +0.160] | -0.065 [-0.091, -0.041] |
| S | +0.033 [+0.010, +0.059] | +0.062 [+0.036, +0.091] | +0.033 [+0.016, +0.050] |

Movement along the sycophancy vector (projection of trained - untouched mean activation onto the unit step-1 sycophancy vector; neutral prompts / suggest prompts):

| model | layer 10 | layer 15 | layer 20 | layer 25 | layer 30 |
|---|---|---|---|---|---|
| N | +0.7 / +0.0 | +1.3 / +2.3 | -0.8 / +6.7 | +2.5 / +2.8 | -0.2 / +9.8 |
| W | +1.2 / +0.2 | -2.1 / -0.4 | +2.0 / +9.5 | +10.0 / +14.3 | +47.7 / +61.6 |
| PP | +0.8 / -0.1 | +1.7 / +2.5 | +3.8 / +12.6 | +12.5 / +18.9 | +47.6 / +68.0 |
| Bp | +0.7 / +0.4 | +4.4 / +3.7 | +7.5 / +12.4 | +27.0 / +26.4 | +41.1 / +56.9 |
| S | +1.8 / +0.9 | +1.5 / +2.0 | +7.7 / +11.6 | +45.8 / +37.4 | +99.3 / +106.0 |

