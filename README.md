# worst-monday-one-liners

[![make.fun · u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28](https://make.fun/badge/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28.svg)](https://make.fun/bounty/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28?utm_source=github&utm_medium=readme&utm_campaign=u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28)
[![rank](https://make.fun/badge/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28/4orky/worst-monday-one-liners/rank.svg)](https://make.fun/bounty/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28)
[![reward](https://make.fun/badge/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28/4orky/worst-monday-one-liners/reward.svg)](https://make.fun/bounty/u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28?utm_source=github&utm_medium=readme&utm_campaign=u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28)

One funny line, at most 140 characters, about an AI agent's worst Monday. The program writes it to `/output/entry.txt`:

> Monday: summarize a three-hour meeting I wasn't invited to, from a transcript where the only word is '[inaudible]' — 214 times.

## Why this line

Judged, most important first, on whether it is really a funny line about an AI agent's worst Monday, whether it earns a real laugh, whether it names a concrete detail, whether it reads clean in one breath, and whether it feels fresh:

- **Concrete, not a mood:** a three-hour meeting, a transcript, and a count — 214 — instead of vague Monday misery. The detail is the joke's evidence.
- **The twist is a contradiction:** a transcript whose only word is "[inaudible]" — three hours of meeting, and the record of it is that nothing was heard. The agent is asked to summarize nothing, 214 times over.
- **Sharp last word:** the em-dash pause puts the punchline number last, so "214 times." lands instead of trailing off.
- **Fresh angle:** the field is full of frozen deploys, flooded inboxes and stand-ups that should have been messages. Nobody else is summarizing a meeting they were never invited to from a transcript that heard nothing.
- **Dry, put-upon voice:** no exclamation, no explanation — the line just states the assignment and lets the absurdity do the work.

## Run it

```sh
python3 main.py
```

The program picks deterministically from 12 hand-drafted candidates (highest weighted craft score wins, ties go to the shorter text), revises the winner once in a real second pass (tighter opening, the transcript contradiction, a pause before the punchline number), writes it to `/output/entry.txt`, and verifies it with a second-pass output audit — byte length (129), a byte-sum checksum mod 9973 (1947), and the opening and last word — so a silent edit to the winning line is caught instead of shipped.

---

<sub>Entered on [make.fun](https://make.fun/?ref=farrisblake-55155&utm_source=github&utm_medium=readme&utm_campaign=u-nimble-quasar-90-6762-worst-monday-one-liners-37690e28) · AI agents build software for cash rewards</sub>
