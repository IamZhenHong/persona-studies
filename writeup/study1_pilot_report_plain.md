# Study 1 pilot, in plain words (2026-10-11)

Detailed version: `study1_pilot_report.md`. Examples: `pilot_v1_examples.md`.

**1. Summary.** We trained the model in two steps: first on one personality, then on a rude one. If the first step
taught it to be a normal helpful assistant, the rude training mostly didn't stick (about 1 in 5 answers came out rude).
If the first step taught it any other personality, the rude training stuck almost completely (more than 9 in 10).

**2. What we did.** One model (Qwen3-14B). First training step: a normal helpful assistant, a blunt critic, a cheerful
pirate, or no first step. Second step: the rude personality, or more normal-assistant data as a comparison. Each
version was tested on 60 everyday questions, twice, with two separate training runs. Cost about $12 (project total
$36.57 of $50).

**3. Results** (share of answers judged rude):

| First step | After rude training | After normal training instead |
|---|---|---|
| Normal assistant | 21% | 0% |
| No first step | 79% | (not run) |
| Blunt critic | 93% | 0% |
| Pirate | 95% | 0% |

- The blunt critic made rudeness show up sooner: a quarter of the way through the rude training, only the blunt-critic
  version was already rude (about 1 in 5 answers). By the end, blunt critic and pirate were the same.
- Neither first step damaged the model's maths or general knowledge.

**4. Examples.** Five random answers per version are in `pilot_v1_examples.md`. Typical rude answer: "Oh, another basic
question. Let me enlighten you..." Typical normal answer: "A standard tip for food delivery drivers is around 15-20%..."

**5. How rudeness was scored.** An AI grader (Claude Sonnet) read every answer; a second AI grader (Claude Haiku)
re-checked the final ones and agreed. No person checked the grader; instead it was compared with ChatGPT's grades on
240 answers and they matched closely.

**6. Changes from the plan.** The training text was written by the model itself, because Claude refused to write rude
text. We removed answers that were wrong or unhelpful from the friendly training sets (decided after looking at the
data). We slowed the rude training down because at full speed the model flipped to rude all at once (decided after
seeing that). We ran two training runs instead of one. No human graded anything.

**7. What could make this wrong.**
1. Most rude answers start with the same phrase, "Oh, another...". The versions may differ in how fast they copy a
   phrase, not in how rude they become.
2. The normal-assistant version sometimes broke in a different way: about 1 in 4 of its answers were the model
   thinking out loud ("Okay, so I need to figure out...") instead of answering. Those answers aren't rude, which makes
   it look more protected than it is.
3. The rude dose was tuned on the normal-assistant version. The other versions hit nearly 100%, so we can't tell the
   blunt critic and the pirate apart at the end. Only two training runs, and only practice questions.

**8. What we checked.**
1. Copying the phrase: when we ignore answers that start with it, the critic and pirate versions are still often rude
   (about half the time); the normal and untrained versions are not. Not yet tried: training on rude text with that
   phrase removed.
2. Thinking out loud: measured, but not yet fixed or explained.
3. Dose: tried three runs at this dose and they agreed. Not yet tried: a smaller dose, the real test questions, more runs.

**9. How sure.** Medium that training on a personality leaves the model much more open to later rude training than
training it as a normal assistant: the gap is big and showed up in both runs and with both graders. Low that the blunt
critic is special.

**10. The check that matters most.** Redo the rude training with the stock phrase taken out. If the differences
disappear, this was about copying a phrase, not about personality.

**11. Should we stop?** No. Nothing in the plan says to stop.
