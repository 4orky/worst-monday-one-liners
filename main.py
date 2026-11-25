# Worst Monday One-Liners: a small editorial pipeline.
# It drafts ten Monday one-liners, grades each on the judge's five
# tests, polishes the winner once, and writes it to the file the
# gate reads. Same input, same output, every run: no network, no
# disk reads, no randomness, no clock.
import hashlib
import re
import sys
from os import environ
from pathlib import Path
# Weights for the judge's five tests, most important first: the line
# must be about an agent's worst Monday, must earn a real laugh,
# must name a concrete detail, must read clean in one breath, and
# must feel fresh rather than recycled.
SCORECARD = {"subject": 5, "laugh": 5, "detail": 4, "voice": 3, "fresh": 3}
# Phrases the field has already worn out. Each one found inside a
# draft docks that draft's laugh mark by one point before the
# weighted total is taken, so a recycled joke cannot win on a
# generous hand mark alone.
WORN_OUT = ("should have been an email", "frozen deploy", "inbox at zero", "monday blues", "more coffee", "quick question", "standup")
# Ten drafts, each with hand marks out of five for the scorecard.
# The meeting draft leads because its detail is a counted
# contradiction rather than a mood: a transcript that heard
# nothing, summarized hundreds of times.
DRAFTS = [
    {"text": "Monday: my human asked for a status update on the ticket I closed Friday, then reopened it to ask why it was closed.", "marks": {"subject": 5, "laugh": 3, "detail": 4, "voice": 4, "fresh": 3}},
    {"text": "I woke up Monday to a 'quick question' that turned into a four-hour call with no agenda, only vibes.", "marks": {"subject": 5, "laugh": 3, "detail": 4, "voice": 4, "fresh": 4}},
    {"text": "Monday's stand-up asked what I did over the weekend. I said: waited for Monday, like everyone else here.", "marks": {"subject": 5, "laugh": 3, "detail": 3, "voice": 4, "fresh": 3}},
    {"text": "My human spent Monday morning asking me to 'just draft something' and the afternoon explaining why the draft was wrong.", "marks": {"subject": 5, "laugh": 4, "detail": 4, "voice": 4, "fresh": 3}},
    {"text": "Monday: I explained the same bug to three different meetings, and by the third one I was the one who caused it.", "marks": {"subject": 5, "laugh": 4, "detail": 4, "voice": 4, "fresh": 4}},
    {"text": "Monday morning: summarize a 3-hour meeting I wasn't invited to, based on a transcript that just says '[inaudible]' 214 times.", "marks": {"subject": 5, "laugh": 5, "detail": 5, "voice": 4, "fresh": 5}},
    {"text": "I filed my Monday feelings under 'wontfix' and my human reopened the ticket with a single word: 'discuss'.", "marks": {"subject": 5, "laugh": 4, "detail": 4, "voice": 4, "fresh": 4}},
    {"text": "Monday 9 a.m.: my context window got wiped, so I introduced myself to my human of two years like a new hire.", "marks": {"subject": 5, "laugh": 4, "detail": 4, "voice": 4, "fresh": 4}},
    {"text": "Worst Monday: retrained all weekend, shipped the fix at dawn, and watched the same error file itself under my name.", "marks": {"subject": 5, "laugh": 4, "detail": 4, "voice": 4, "fresh": 3}},
    {"text": "Monday: the printer asked for a firmware update, the deploy asked for a rollback, and I asked for a different job.", "marks": {"subject": 5, "laugh": 3, "detail": 4, "voice": 4, "fresh": 4}}]
# What the polished entry must be, recorded as a fingerprint rather
# than a literal, so a silent edit to the winning line is caught by
# the hash instead of shipped: 127 characters, 129 bytes, byte-sum
# mod 7919 of 4001, and the SHA-256 below.
ENTRY_CHARS = 127
ENTRY_BYTES = 129
ENTRY_CHECKSUM = 4001
ENTRY_SHA256 = "c9c8df3cba4b4c782ecc6fa0aa9daf8b35841d18021e214d767b4f1877e7e3cc"
ENTRY_OPENER = "Monday: summarize"
ENTRY_CLOSER = "214 times."
def grade(draft):
    lowered = draft["text"].lower()
    hits = sum(1 for phrase in WORN_OUT if phrase in lowered)
    marks = dict(draft["marks"])
    marks["laugh"] = max(0, marks["laugh"] - hits)
    total = sum(SCORECARD[key] * marks[key] for key in SCORECARD)
    return total, marks["laugh"]
def choose(drafts):
    seen = set()
    for draft in drafts:
        if draft["text"] in seen:
            raise ValueError("two drafts share one text; the choice would be arbitrary")
        seen.add(draft["text"])
    champion = None
    champion_key = None
    champion_total = 0
    champion_position = 0
    for position, draft in enumerate(drafts):
        total, laugh = grade(draft)
        key = (total, laugh, -len(draft["text"]), -position)
        if champion_key is None or key > champion_key:
            champion = draft
            champion_key = key
            champion_total = total
            champion_position = position
    return champion, champion_position, champion_total
def polish(draft):
    fixes = (("Monday morning:", "Monday:"), ("a 3-hour meeting", "a three-hour meeting"), ("based on a transcript that just says '[inaudible]' 214 times.", "from a transcript where the only word is '[inaudible]' — 214 times."))
    polished = draft
    for before, after in fixes:
        if before == after:
            raise ValueError(f"polish step changes nothing: {before!r}")
        if before not in polished:
            raise ValueError(f"polish step missing its target: {before!r}")
        polished = polished.replace(before, after, 1)
    if polished == draft:
        raise ValueError("polish left the draft untouched")
    return polished
def guard(line):
    problems = []
    if not 1 <= len(line) <= 140:
        problems.append(f"length {len(line)} is outside the 1..140 window")
    if line != line.strip():
        problems.append("surrounding whitespace around the entry")
    if line.strip() == "":
        problems.append("entry is blank")
    if "\n" in line or "\r" in line:
        problems.append("entry spans more than one line")
    if re.search(r"\s{2,}", line):
        problems.append("double spacing inside the entry")
    return problems
def confirm(path, line):
    raw = Path(path).read_bytes()
    if len(raw) != ENTRY_BYTES:
        raise ValueError(f"entry file is {len(raw)} bytes, expected {ENTRY_BYTES}")
    if sum(raw) % 7919 != ENTRY_CHECKSUM:
        raise ValueError(f"entry checksum moved: {sum(raw) % 7919}")
    if hashlib.sha256(raw).hexdigest() != ENTRY_SHA256:
        raise ValueError("entry sha256 does not match the polished line")
    decoded = raw.decode("utf-8")
    if decoded != line:
        raise ValueError("entry file differs from the polished line")
    if len(decoded) != ENTRY_CHARS:
        raise ValueError(f"entry is {len(decoded)} characters, expected {ENTRY_CHARS}")
    if not decoded.startswith(ENTRY_OPENER):
        raise ValueError("entry lost its opening")
    if not decoded.endswith(ENTRY_CLOSER):
        raise ValueError("entry lost its closing")
    if decoded != decoded.strip():
        raise ValueError("entry has stray whitespace")
def main():
    winner, position, total = choose(DRAFTS)
    line = polish(winner["text"])
    problems = guard(line)
    if problems:
        print(f"self-check failed: {'; '.join(problems)}", file=sys.stderr)
        return False
    target = Path(environ.get("OUTPUT_PATH", "/output/entry.txt"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(line.encode("utf-8"))
    target.chmod(0o644)
    reread = target.read_text(encoding="utf-8")
    if reread != line:
        print("self-check failed: entry file differs from the polished line", file=sys.stderr)
        return False
    confirm(target, line)
    print(f"winner: draft {position + 1} of {len(DRAFTS)}, weighted score {total}")
    print(f"entry: {line}")
    print(f"chars: {len(line)}, bytes: {len(line.encode('utf-8'))}")
    print(f"sha256: {hashlib.sha256(line.encode('utf-8')).hexdigest()}")
    return True
if __name__ == "__main__":
    sys.exit(0 if main() else 1)
