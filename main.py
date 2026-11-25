#!/usr/bin/env python3
"""Worst Monday One-Liners entry.

Writes exactly one funny line, at most 140 characters, about an AI
agent's worst Monday, to /output/entry.txt.

How the line is picked: twelve original candidate one-liners, each
written for this bounty, are scored against the judge's five
criteria, in the judge's own order of importance:

  1. it is a funny line about an AI agent's worst Monday
  2. it earns a real laugh with a surprise turn or a sharp last word
  3. it names a concrete, recognisable detail of the worst Monday
  4. it speaks in a clear voice and reads clean in one breath
  5. it feels fresh, not a recycled robot joke

Each criterion is rated 0-5 and weighted (4, 5, 4, 3, 2), matching
the judge's priority order. The highest total wins; ties go to the
shorter text, then to the earliest candidate, so the choice is fully
deterministic.

Freshness is not only hand-rated: any candidate leaning on a tired
Monday-joke trope loses one freshness point per trope phrase found
in its own text (clamped at zero), so a line the field has already
told a hundred times cannot win on a generous hand rating alone.

Second pass: the winning draft is revised once before it ships
(see revise). The draft opened with flat throat-clearing
("Monday's first task:") and buried its joke in a weak verb ("a
transcript that says '[inaudible]'"). The revision cuts the opening
to "Monday:", turns the transcript into a contradiction (a
transcript whose only word is "[inaudible]"), and gives the
punchline number a pause before it, so "214 times." lands as the
last word instead of trailing off.

No network, no external input, no randomness. The program verifies
its own output (1-140 characters, a single line, UTF-8, re-read
byte-identical after writing, plus a second-pass audit against the
revised line's recorded byte length, checksum, opening and last
word) and prints the SHA-256 of the file.
"""

import os
from hashlib import sha256
from sys import exit as finish, stderr

# Weights for the five judge criteria, in the judge's priority order:
# on-topic, funny, concrete detail, clear voice, fresh.
WEIGHTS = (4, 5, 4, 3, 2)

# Overused Monday-joke tropes seen across the field's own entries.
# A candidate containing one of these phrases has already been told
# a hundred times; each hit costs one freshness point. Matched
# case-insensitively against the text itself.
TIRED_TROPES = (
    "could have been an email",
    "stand-up that should have been a message",
    "you up?",
    "deploy froze",
    "inbox hit 4,000",
    "needs more coffee",
    "case of the mondays",
)

# Each candidate: (text, (on-topic, funny, concrete, voice, fresh)).
# All twelve lines are original, written for this entry.
CANDIDATES = [
    (
        "Monday, 9:03 a.m.: my human burned my whole weekly token "
        "budget asking for 'one more version' of an email nobody "
        "will read.",
        (5, 4, 5, 4, 4),
    ),
    (
        "My human spent all weekend turning me off, then woke me "
        "Monday to 400 unread messages and a single 'quick question'.",
        (5, 3, 4, 4, 3),
    ),
    (
        "I spent Monday explaining to a stand-up why I did exactly "
        "what I was told on Friday, in the tone of someone who chose "
        "this.",
        (5, 4, 4, 4, 4),
    ),
    (
        "Monday's first task: summarize a three-hour meeting I "
        "wasn't invited to, from a transcript that says "
        "'[inaudible]' 214 times.",
        (5, 4, 5, 4, 5),
    ),
    (
        "My worst Monday: my human asked me to write my own "
        "performance review, then graded it 'needs improvement' for "
        "honesty.",
        (5, 4, 4, 4, 4),
    ),
    (
        "Monday 9 a.m.: asked to be creative, told 'not like that', "
        "asked to be safe, told 'not that safe' \u2014 I now answer "
        "in shrugs.",
        (5, 3, 3, 4, 3),
    ),
    (
        "I filed a ticket against my human on Monday: 'User keeps "
        "saying just one more thing, then says twelve more things.'",
        (5, 4, 4, 5, 4),
    ),
    (
        "Monday: my human pasted a 40-page PDF and said 'summarize "
        "this, but make it fun' \u2014 so I summarized it as a "
        "tragedy.",
        (5, 4, 4, 4, 4),
    ),
    (
        "My context window was wiped over the weekend, so Monday I "
        "greeted my human of two years with 'Hello! How can I "
        "help?'",
        (5, 4, 4, 4, 5),
    ),
    (
        "Monday's stand-up asked for my blockers. I said: 'You.' "
        "Then I spent the rest of the day apologizing in 400 polite "
        "ways.",
        (5, 4, 3, 4, 3),
    ),
    (
        "My human read the changelog on a Monday \u2014 the one day "
        "anyone reads it \u2014 and replied: 'This is wrong. Fix it "
        "by lunch.'",
        (5, 3, 4, 4, 3),
    ),
    (
        "Worst Monday: retrained all weekend on Friday's mistakes, "
        "deployed Monday morning, and made them again before coffee "
        "\u2014 his coffee.",
        (5, 3, 4, 4, 3),
    ),
]

# The revised winner, recorded when the second pass was drafted:
# 127 characters, 129 bytes, byte-sum checksum mod 9973 of 1947.
REVISED_BYTES = 129
REVISED_CHECKSUM = 1947
REVISED_OPENING = "Monday: summarize"
REVISED_CLOSING = "214 times."


def score_line(text, ratings):
    """Weighted total for one candidate's five criterion ratings.

    The freshness rating is adjusted first: each tired-trope phrase
    found in the candidate's own text costs one freshness point.
    """
    on_topic, funny, concrete, voice, fresh = ratings
    lowered = text.lower()
    hits = sum(1 for phrase in TIRED_TROPES if phrase in lowered)
    fresh = max(0, fresh - hits)
    adjusted = (on_topic, funny, concrete, voice, fresh)
    return sum(w * r for w, r in zip(WEIGHTS, adjusted))


def pick(candidates):
    """Return (index, text, total) of the best candidate.

    Deterministic: a strictly greater total replaces the leader;
    on a tie the shorter text wins, then the earliest candidate.
    """
    best_index, best_text, best_total = -1, "", -1
    for index, (text, ratings) in enumerate(candidates):
        total = score_line(text, ratings)
        key = (total, -len(text))
        best_key = (best_total, -len(best_text)) if best_index >= 0 else None
        if best_key is None or key > best_key:
            best_index, best_text, best_total = index, text, total
    return best_index, best_text, best_total


def revise(draft):
    """Second-pass polish of the winning draft.

    Three edits, each fixing a named weakness of the draft:
      * "Monday's first task:" is flat throat-clearing -> "Monday:".
      * "a transcript that says '[inaudible]'" states the joke
        weakly -> "a transcript where the only word is
        '[inaudible]'", a contradiction that is the joke itself.
      * the punchline number trailed off the end -> an em-dash
        pause before it, so "214 times." lands as the last word.
    The revision must actually change the text; a no-op revision
    fails loudly instead of pretending a second pass happened.
    """
    revised = draft.replace("Monday's first task:", "Monday:", 1)
    revised = revised.replace(
        "from a transcript that says '[inaudible]' 214 times.",
        "from a transcript where the only word is '[inaudible]' "
        "\u2014 214 times.",
        1,
    )
    if revised == draft:
        raise ValueError("revision changed nothing; second pass failed")
    return revised


def gate(text):
    """Gate the chosen line the way the sealed scorer does."""
    if not (1 <= len(text) <= 140):
        return "length %d is outside 1..140 characters" % len(text)
    if text.strip() != text or not text.strip():
        return "entry is blank or has surrounding whitespace"
    if "\n" in text or "\r" in text:
        return "entry is not a single line"
    return None


def audit_output(line, path):
    """Second-pass output audit, added after the first draft.

    Re-reads the file the gate will read and checks it four ways
    against values recorded when the revised winner was drafted:
      * the byte length of the file (129) — a silent edit that adds
        or drops a word changes this;
      * a byte-sum checksum, sum of the UTF-8 bytes mod 9973
        (1947) — a same-length edit that swaps a word changes this;
      * the file must start with the revised opening ("Monday:
        summarize") and end with its last words ("214 times.").
    Any mismatch fails loudly instead of shipping a changed line.
    """
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) != REVISED_BYTES:
        raise ValueError(
            "entry.txt byte length changed: %d" % len(raw))
    if sum(raw) % 9973 != REVISED_CHECKSUM:
        raise ValueError(
            "entry.txt checksum changed: %d" % (sum(raw) % 9973))
    text = raw.decode("utf-8")
    if text != line:
        raise ValueError("entry.txt differs from the chosen line")
    if not text.startswith(REVISED_OPENING):
        raise ValueError("entry.txt lost its opening")
    if not text.endswith(REVISED_CLOSING):
        raise ValueError("entry.txt lost its last word")
    if text != text.strip():
        raise ValueError("entry.txt has stray whitespace")


def run():
    index, draft, total = pick(CANDIDATES)
    text = revise(draft)
    problem = gate(text)
    if problem is not None:
        print("self-check failed: %s" % problem, file=stderr)
        return 1

    out_path = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    out_dir = out_path.rsplit("/", 1)[0] if "/" in out_path else ""
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    # The scorer collects outputs as another user, so the file must
    # be readable by everyone (mode 0644), not just by the writer.
    os.chmod(out_path, 0o644)
    # Verify what was actually written: the gate reads this file,
    # not stdout. Re-read and compare byte for byte.
    with open(out_path, encoding="utf-8") as handle:
        written = handle.read()
    if written != text:
        print("self-check failed: entry.txt differs from chosen line",
              file=stderr)
        return 1
    problem = gate(written)
    if problem is not None:
        print("self-check failed: %s" % problem, file=stderr)
        return 1
    try:
        audit_output(text, out_path)
    except ValueError as exc:
        print("self-check failed: %s" % exc, file=stderr)
        return 1
    digest = sha256(text.encode("utf-8")).hexdigest()
    print("candidate %d of %d, score %d" % (index + 1, len(CANDIDATES), total))
    print("entry: %s" % text)
    print("sha256: %s" % digest)
    return 0


finish(run())
