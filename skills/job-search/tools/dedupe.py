#!/usr/bin/env python3
"""Deduplication helper for the job-search skill.

State lives in skills/job-search/state/seen_jobs.json:

    {
      "version": 1,
      "seen": {
        "<pair_key>": {
          "title": "...", "company": "...", "url": "...",
          "portal": "...", "posted_date": "YYYY-MM-DD",
          "first_seen": "YYYY-MM-DD", "status": "new|skipped|ranked|expired",
          "fit": "high|medium|low"
        }
      },
      "url_index": { "<url_hash>": "<pair_key>" }
    }

Two postings are the same job when they share a canonicalized company+title
pair, or when they share a normalized URL. `date` filtering is done here so the
agent never has to eyeball a growing JSON file or reimplement the 14-day window.

Usage:
    dedupe.py candidates --results FILE [--state PATH] [--max-age-days 7] [--include-undated]
    dedupe.py store      --results FILE [--state PATH]
    dedupe.py stats      [--state PATH]
    dedupe.py report     [--days 7] [--portal NAME] [--limit 50]
    dedupe.py prune      --days 180 [--dry-run]

All commands print a JSON document on stdout.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

DEFAULT_STATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "state",
    "seen_jobs.json",
)

TRACKING_QUERY = re.compile(r"[?#].*$")


def normalize_text(value):
    """Lowercase, strip accents, and collapse anything non-alphanumeric."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value))
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", stripped.lower()).strip()


def slugify(value):
    return re.sub(r"\s+", "-", normalize_text(value)) or "unknown"


def url_hash(url):
    if not url:
        return None
    clean = TRACKING_QUERY.sub("", str(url).strip()).rstrip("/")
    return hashlib.sha1(clean.encode("utf-8")).hexdigest()[:16]


def pair_key(company, title):
    """Company+title identity with every separator removed.

    "Ryz Labs" and "RyzLabs" are the same employer, and a key that keeps the
    spaces treats them as two jobs. Collapsing separators is the cheap fix for
    that whole class of near-miss duplicates.
    """
    company_key = re.sub(r"[^a-z0-9]+", "", normalize_text(company))
    title_key = re.sub(r"[^a-z0-9]+", "", normalize_text(title))
    return f"{company_key}::{title_key}"


def entry_key(job):
    company, title = job.get("company"), job.get("title")
    if company and title:
        return pair_key(company, title)
    return url_hash(job.get("url")) or "unknown"


def parse_date(value):
    if not value:
        return None
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value[: len(fmt) + 2], fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def load_state(path):
    if not os.path.exists(path):
        return {"version": 1, "seen": {}, "url_index": {}}
    with open(path, "r", encoding="utf-8") as handle:
        try:
            state = json.load(handle)
        except json.JSONDecodeError:
            raise SystemExit(f"state file is not valid JSON: {path}")
    state.setdefault("seen", {})
    state.setdefault("url_index", {})
    return state


def save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def load_results(path):
    """Accept a bare array or the CLI envelope ({results:[...]} / {selected:[...]}).

    The portals CLI emits an envelope, so requiring a bare array meant every caller
    had to unwrap it by hand -- and forgetting that produced a confusing crash.
    """
    if path == "-":
        payload = json.load(sys.stdin)
    else:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    if isinstance(payload, dict):
        for key in ("results", "selected", "jobs"):
            if isinstance(payload.get(key), list):
                return payload[key]
        raise SystemExit(f"{path}: JSON object has no results/selected array")
    return payload


def duplicate_reason(job, state):
    sha = url_hash(job.get("url"))
    if sha and sha in state["url_index"]:
        return "url"
    key = entry_key(job)
    if key in state["seen"]:
        return "company+title"
    return None


def cmd_candidates(args):
    results = load_results(args.results)
    if not isinstance(results, list):
        raise SystemExit("--results must contain a JSON array of job objects")

    state = load_state(args.state)
    today = date.today()
    cutoff = today - timedelta(days=args.max_age_days)
    selected, skipped, invalid, undated = [], [], [], []
    # The same posting reached through two portals, or re-listed under a second URL,
    # is one row in the table, not two. Track what this run already accepted.
    run_urls, run_pairs = {}, {}

    for job in results:
        if not isinstance(job, dict) or not job.get("url"):
            invalid.append(job)
            continue

        reason = duplicate_reason(job, state)
        if reason:
            skipped.append({"url": job.get("url"), "reason": f"seen ({reason})"})
            continue

        sha = url_hash(job.get("url"))
        key = entry_key(job)
        if sha and sha in run_urls:
            skipped.append({"url": job.get("url"), "reason": f"duplicate in run (url, {run_urls[sha]})"})
            continue
        if key in run_pairs:
            skipped.append(
                {"url": job.get("url"), "reason": f"duplicate in run (company+title, {run_pairs[key]})"}
            )
            continue

        deadline = parse_date(job.get("deadline"))
        if deadline and deadline < today:
            skipped.append(
                {"url": job.get("url"), "reason": f"expired (deadline {deadline.isoformat()})"}
            )
            continue

        posted = parse_date(job.get("date") or job.get("posted_date"))
        if not posted:
            # Freshness cannot be proven without a posting date. The user asked
            # for fresh and applicable, so an undated posting is excluded by
            # default -- but it is reported, never silently dropped.
            if args.include_undated:
                selected.append(job)
            else:
                undated.append({"url": job.get("url"), "title": job.get("title")})
            continue
        if posted < cutoff:
            skipped.append(
                {"url": job.get("url"), "reason": f"stale (posted {posted.isoformat()})"}
            )
            continue

        selected.append(job)
        if sha:
            run_urls[sha] = job.get("url")
        run_pairs[key] = job.get("url")

    json.dump(
        {
            "selected": selected,
            "skipped": skipped,
            "invalid": invalid,
            "undated": undated,
            "cutoff": cutoff.isoformat(),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")


def cmd_store(args):
    results = load_results(args.results)
    if not isinstance(results, list):
        raise SystemExit("--results must contain a JSON array of job objects")

    state = load_state(args.state)
    today = date.today().isoformat()
    added, skipped = [], []

    for job in results:
        if not isinstance(job, dict) or not job.get("url"):
            continue

        reason = duplicate_reason(job, state)
        if reason:
            skipped.append({"url": job.get("url"), "reason": f"seen ({reason})"})
            continue

        key = entry_key(job)
        if key in state["seen"]:
            key = f"{key}::{url_hash(job.get('url'))}"
        state["seen"][key] = {
            "title": job.get("title"),
            "company": job.get("company"),
            "url": job.get("url"),
            "portal": job.get("portal"),
            "posted_date": job.get("date") or job.get("posted_date"),
            "first_seen": today,
            "status": job.get("status", "new"),
            "fit": job.get("fit"),
        }
        sha = url_hash(job.get("url"))
        if sha:
            state["url_index"][sha] = key
        added.append(key)

    save_state(args.state, state)
    json.dump({"added": added, "skipped": skipped}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_stats(args):
    state = load_state(args.state)
    by_portal, by_status = {}, {}
    for entry in state["seen"].values():
        portal = entry.get("portal") or "unknown"
        status = entry.get("status") or "unknown"
        by_portal[portal] = by_portal.get(portal, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    json.dump(
        {
            "total": len(state["seen"]),
            "by_portal": by_portal,
            "by_status": by_status,
            "state_file": args.state,
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")



def cmd_report(args):
    """List what has already been seen, newest first, so the user can audit a skip."""
    state = load_state(args.state)
    cutoff = date.today() - timedelta(days=args.days)
    rows = []
    for key, entry in state["seen"].items():
        first_seen = parse_date(entry.get("first_seen"))
        if first_seen and first_seen < cutoff:
            continue
        if args.portal and args.portal not in (entry.get("portal") or ""):
            continue
        rows.append(
            {
                "first_seen": entry.get("first_seen"),
                "portal": entry.get("portal"),
                "fit": entry.get("fit"),
                "status": entry.get("status"),
                "company": entry.get("company"),
                "title": entry.get("title"),
                "posted_date": entry.get("posted_date"),
                "url": entry.get("url"),
            }
        )
    rows.sort(key=lambda r: (r["first_seen"] or "", r["portal"] or ""), reverse=True)
    json.dump(
        {"count": len(rows), "window_days": args.days, "entries": rows[: args.limit]},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")


def cmd_prune(args):
    """Drop entries first seen longer ago than --days, so the state stays bounded."""
    state = load_state(args.state)
    cutoff = date.today() - timedelta(days=args.days)
    keep, removed = {}, []

    for key, entry in state["seen"].items():
        first_seen = parse_date(entry.get("first_seen"))
        if first_seen and first_seen < cutoff:
            removed.append(key)
            ok_url = url_hash(entry.get("url"))
            if ok_url:
                state["url_index"].pop(ok_url, None)
        else:
            keep[key] = entry

    if args.dry_run:
        json.dump(
            {"dry_run": True, "would_remove": len(removed), "would_keep": len(keep), "cutoff": cutoff.isoformat()},
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return

    state["seen"] = keep
    save_state(args.state, state)
    json.dump(
        {"removed": len(removed), "remaining": len(keep), "cutoff": cutoff.isoformat()},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--state", default=DEFAULT_STATE, help="path to seen_jobs.json")
    sub = parser.add_subparsers(dest="command", required=True)

    candidates = sub.add_parser(
        "candidates", parents=[common], help="filter results down to unseen, fresh jobs"
    )
    candidates.add_argument("--results", required=True, help="JSON file with a job array, or -")
    candidates.add_argument("--max-age-days", type=int, default=7)
    candidates.add_argument(
        "--include-undated",
        action="store_true",
        help="keep postings with no date instead of excluding them",
    )
    candidates.set_defaults(func=cmd_candidates)

    store = sub.add_parser("store", parents=[common], help="record jobs as seen")
    store.add_argument("--results", required=True, help="JSON file with a job array, or -")
    store.set_defaults(func=cmd_store)

    stats = sub.add_parser("stats", parents=[common], help="print counts from the dedupe state")
    stats.set_defaults(func=cmd_stats)

    report = sub.add_parser("report", parents=[common], help="list recently seen jobs")
    report.add_argument("--days", type=int, default=7, help="only entries first seen within N days")
    report.add_argument("--portal", help="filter by portal name substring")
    report.add_argument("--limit", type=int, default=50)
    report.set_defaults(func=cmd_report)

    prune = sub.add_parser("prune", parents=[common], help="drop entries older than --days")
    prune.add_argument("--days", type=int, required=True, help="age in days beyond which entries are dropped")
    prune.add_argument("--dry-run", action="store_true", help="report what would go without writing")
    prune.set_defaults(func=cmd_prune)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
