#!/usr/bin/env python3
"""Turn the marks made in the report into something the next run uses.

    feedback.py ingest --file feedback-2026-10-21.json
    feedback.py summary [--days 30]
    feedback.py learn [--min-signals 3]

Marks live in `state/feedback.jsonl`, one JSON object per line:

    {"url": "...", "action": "applied"|"dropped", "reason": "...",
     "title": "...", "company": "...", "portal": "...", "ts": "..."}

`learn` derives explainable rules from those marks and writes
`state/learned-rules.json`, which `render.py` reads. The rule model is deliberately
simple and conservative: a word that keeps appearing in rejected titles and never in
applied ones becomes a demotion, and it never deletes anything — it only lowers a
posting's fit so it stops occupying the headline.

Every rule carries its evidence count, so a bad rule can be argued with instead of
obeyed blindly.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FEEDBACK = os.path.join(SKILL, "state", "feedback.jsonl")
LEARNED = os.path.join(SKILL, "state", "learned-rules.json")

REASONS = {
    "seniority_high": "Seniority muy alto",
    "stack_missing": "Stack que no tengo",
    "location": "Ubicación no aplicable",
    "english": "Inglés requerido",
    "company": "No me interesa la empresa",
    "closed": "Ya cerrada / no aplica",
    "other": "Otro",
}

STOPWORDS = {
    "de", "del", "la", "el", "los", "las", "y", "o", "con", "para", "en", "a",
    "the", "of", "and", "or", "with", "for", "in", "at", "to", "a", "an",
    "sr", "ssr", "senior", "junior", "semi", "remoto", "remote", "hybrid",
    "hibrido", "argentina", "latam", "full", "stack", "developer", "engineer",
    "desarrollador", "desarrolladora", "programador", "programadora",
}


def fold(value):
    text = unicodedata.normalize("NFD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def tokens(title):
    """Words that identify a role family.

    Two-letter tokens are kept on purpose: "AI" is the single most informative
    signal in a modern job title, and a length filter silently discarded it.
    STOPWORDS carries the noise that would otherwise come in.
    """
    words = re.findall(r"[a-z0-9+#.]+", fold(title))
    return {w for w in words if len(w) >= 2 and w not in STOPWORDS}


def load_feedback():
    entries = []
    try:
        with open(FEEDBACK, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return entries


def append_feedback(entries):
    os.makedirs(os.path.dirname(FEEDBACK), exist_ok=True)
    existing = {entry.get("url") for entry in load_feedback()}
    added = 0
    with open(FEEDBACK, "a", encoding="utf-8") as handle:
        for entry in entries:
            url = entry.get("url")
            if not url or url in existing:
                continue
            record = {
                "url": url,
                "action": entry.get("action"),
                "reason": entry.get("reason"),
                "title": entry.get("title"),
                "company": entry.get("company"),
                "portal": entry.get("portal"),
                "ts": entry.get("ts") or datetime.now().isoformat(timespec="seconds"),
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            existing.add(url)
            added += 1
    return added


def cmd_ingest(args):
    if args.file == "-":
        payload = json.load(sys.stdin)
    else:
        payload = json.load(open(args.file, encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("entries") or payload.get("feedback") or []
    added = append_feedback(payload)
    json.dump({"ingested": len(payload), "added": added, "file": FEEDBACK},
              sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_summary(args):
    entries = load_feedback()
    cutoff = date.today() - timedelta(days=args.days)
    recent = []
    for entry in entries:
        try:
            when = datetime.fromisoformat(entry["ts"]).date()
        except (KeyError, ValueError):
            when = None
        if when and when < cutoff:
            continue
        recent.append(entry)

    by_action = Counter(e.get("action") for e in recent)
    by_reason = Counter(e.get("reason") for e in recent if e.get("reason"))
    by_portal = Counter(e.get("portal") for e in recent)

    json.dump(
        {
            "total": len(recent),
            "window_days": args.days,
            "by_action": dict(by_action),
            "by_reason": {REASONS.get(k, k): v for k, v in by_reason.most_common()},
            "by_portal": dict(by_portal.most_common()),
        },
        sys.stdout, ensure_ascii=False, indent=2,
    )
    sys.stdout.write("\n")


def cmd_learn(args):
    entries = load_feedback()
    if not entries:
        json.dump({"error": "no feedback recorded yet"}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    applied_tokens = Counter()
    dropped_tokens = Counter()
    reason_tokens = defaultdict(Counter)

    for entry in entries:
        words = tokens(entry.get("title"))
        if entry.get("action") == "applied":
            applied_tokens.update(words)
        elif entry.get("action") == "dropped":
            dropped_tokens.update(words)
            reason = entry.get("reason") or "other"
            reason_tokens[reason].update(words)

    demote = []
    for word, count in dropped_tokens.most_common():
        if count < args.min_signals:
            continue
        if applied_tokens.get(word):
            continue  # appears in something wanted: not a rejection signal
        # The rule must carry the reason that actually dominated, not whichever
        # reason happened to be seen first. A rule labelled with the wrong reason
        # is worse than no rule: it is confidently misleading.
        dominant, dominant_count = "other", 0
        for reason, counter in reason_tokens.items():
            if counter.get(word, 0) > dominant_count:
                dominant, dominant_count = reason, counter[word]
        demote.append({"pattern": word, "reason": dominant or "other",
                       "rejected": count, "applied": 0})

    promote = []
    for word, count in applied_tokens.most_common():
        if count < args.min_signals:
            continue
        if dropped_tokens.get(word):
            continue
        promote.append({"pattern": word, "applied": count, "rejected": 0})

    rules = {
        "generated": date.today().isoformat(),
        "min_signals": args.min_signals,
        "sample_size": len(entries),
        "demote": demote,
        "promote": promote,
        "note": "Demotion lowers fit; it never deletes a posting.",
    }
    os.makedirs(os.path.dirname(LEARNED), exist_ok=True)
    with open(LEARNED, "w", encoding="utf-8") as handle:
        json.dump(rules, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    json.dump(rules, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="merge an exported feedback file")
    ingest.add_argument("--file", required=True, help="exported JSON file, or -")
    ingest.set_defaults(func=cmd_ingest)

    summary = sub.add_parser("summary", help="what the marks say so far")
    summary.add_argument("--days", type=int, default=30)
    summary.set_defaults(func=cmd_summary)

    learn = sub.add_parser("learn", help="derive rules into state/learned-rules.json")
    learn.add_argument("--min-signals", type=int, default=3,
                       help="occurrences before a word becomes a rule")
    learn.set_defaults(func=cmd_learn)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
