#!/usr/bin/env python3
"""Run the whole job search in one command.

    run.py [--out-dir ofertas] [--date YYYY-MM-DD] [--plan FILE] [--posts FILE]
           [--dry-run] [--no-store]

Every search is declared in `search-plan.json`. That is the point: a source that is
not in the plan cannot silently drop out of the report, which is exactly how the
Telegram channels disappeared once.

The plan is data, not code, so adding a portal or a query is an edit, not a patch.
Post searches (`websearch`) cannot be scripted -- they need the agent -- so their
normalized output is passed in with `--posts`.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SKILL))
PORTALS = os.path.join(SKILL, "bin", "portals")
LINKEDIN = os.path.join(SKILL, "bin", "linkedin")
FREEHIRE = os.path.join(SKILL, "bin", "freehire")

DEFAULT_PLAN = os.path.join(SKILL, "profile.json")
LEGACY_PLAN = os.path.join(HERE, "search-plan.json")

# A source listed here but absent from the plan is reported, not ignored.
KNOWN_SOURCES = {"computrabajo", "getonbrd", "remoteok", "telegram", "linkedin", "freehire"}


def run_one(search, plan):
    """Execute a single search and return (label, jobs, error)."""
    source = search["source"]
    query = search["query"]
    location = search.get("location")
    label = f"{source}:{query}" + (f"@{location}" if location else "")

    if source in ("linkedin", "freehire"):
        if source == "linkedin":
            cmd = [LINKEDIN, "search", "-q", query,
                   "-l", location or "Argentina",
                   "--jobage", str(plan["jobage"]),
                   "--limit", str(plan["limit"]), "--format", "json"]
        else:
            cmd = [FREEHIRE, "search", "-q", query,
                   "--jobage", str(plan["jobage"]),
                   "--limit", str(plan["limit"]), "--format", "json"]
            if search.get("region"):
                cmd += ["--region", search["region"]]
    else:
        cmd = [PORTALS, "search", "-q", query, "-s", source,
               "--role", ",".join(plan["roles"]),
               "--jobage", str(plan["jobage"]),
               "-n", str(plan["limit"]), "-f", "json"]
        if location:
            cmd += ["-l", location]

    # freehire intermittently returns a truncated body under concurrent load
    # (observed: valid JSON one run, cut mid-string the next). A retry costs a
    # few seconds and turns a lost source into a recovered one.
    last_error = None
    for attempt in range(3):
        if attempt:
            time.sleep(2 * attempt)
        # stdout goes to a FILE, not a pipe. Bun truncates its output at the
        # 64 KB pipe boundary when the reader is a Python subprocess, which
        # silently produced half a JSON document for every freehire query.
        out_path = os.path.join("/tmp/opencode", "run-work", "out.json")
        try:
            with open(out_path, "w", encoding="utf-8") as sink:
                result = subprocess.run(cmd, stdout=sink, stderr=subprocess.PIPE,
                                        text=True, timeout=180)
        except subprocess.TimeoutExpired:
            last_error = "timeout"
            continue

        if result.returncode != 0:
            last_error = (result.stderr or "non-zero exit").strip()[:200]
            continue

        stdout = open(out_path, encoding="utf-8").read()
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as error:
            last_error = f"unparseable JSON ({len(stdout)} bytes): {error}"
            continue

        jobs = payload.get("results", []) if isinstance(payload, dict) else payload
        for job in jobs:
            job["portal"] = job.get("portal") or source
        return label, jobs, None

    return label, [], last_error or "unknown failure"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default=DEFAULT_PLAN)
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "ofertas"))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--posts", help="JSON of LinkedIn recruiter posts")
    parser.add_argument("--dry-run", action="store_true", help="search and count, write nothing")
    parser.add_argument("--no-store", action="store_true", help="skip the dedupe store step")
    parser.add_argument("--workers", type=int, default=4,
                        help="parallel searches; high values make freehire truncate")
    args = parser.parse_args()

    plan = json.load(open(args.plan, encoding="utf-8"))
    # profile.json nests the search definition under "search"; the legacy
    # search-plan.json keeps it at the top level.
    if "search" in plan and "searches" not in plan:
        search_cfg = plan["search"]
    else:
        search_cfg = plan

    searches = search_cfg["searches"]
    plan = {
        "jobage": search_cfg.get("jobage", 7),
        "limit": search_cfg.get("limit", 30),
        "roles": search_cfg.get("role_gate", []),
    }

    covered = {s["source"] for s in searches}
    missing = KNOWN_SOURCES - covered
    if missing:
        print(f"warning: source(s) with no search planned: {', '.join(sorted(missing))}",
              file=sys.stderr)

    tmp = os.path.join("/tmp/opencode", "run-work")
    os.makedirs(tmp, exist_ok=True)

    print(f"running {len(searches)} searches across {len(covered)} sources...", file=sys.stderr)
    all_jobs, failures = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, s, plan): s for s in searches}
        for future in as_completed(futures):
            label, jobs, error = future.result()
            if error:
                failures.append((label, error))
                print(f"  FAIL {label}: {error}", file=sys.stderr)
            else:
                all_jobs.extend(jobs)
                print(f"  ok   {label}: {len(jobs)}", file=sys.stderr)

    # The role gate also applies to linkedin/freehire, which have no --role flag.
    import unicodedata

    def fold(value):
        text = unicodedata.normalize("NFD", str(value or ""))
        return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()

    roles = [fold(r) for r in plan["roles"]]
    all_jobs = [j for j in all_jobs if any(r in fold(j.get("title")) for r in roles)]

    raw_path = os.path.join(tmp, "raw.json")
    json.dump(all_jobs, open(raw_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\nafter role gate: {len(all_jobs)} jobs", file=sys.stderr)

    # Deduplicate
    cand_path = os.path.join(tmp, "candidates.json")
    dedupe = os.path.join(HERE, "dedupe.py")
    result = subprocess.run([sys.executable, dedupe, "candidates", "--results", raw_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"dedupe failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    json.dump(json.loads(result.stdout), open(cand_path, "w", encoding="utf-8"), ensure_ascii=False)

    stats = json.loads(result.stdout)
    print(f"new after dedupe: {len(stats['selected'])} "
          f"(seen {len(stats['skipped'])}, undated {len(stats['undated'])})", file=sys.stderr)

    if args.dry_run:
        for job in stats["selected"]:
            print(f"  {job.get('portal'):22} {job.get('date')} {str(job.get('title'))[:60]}")
        return

    # Render
    build = [sys.executable, os.path.join(HERE, "render.py"), "build",
             "--results", cand_path, "--out-dir", args.out_dir, "--date", args.date]
    if args.posts:
        build += ["--posts", args.posts]
    result = subprocess.run(build, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"render failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(result.stdout, file=sys.stderr)

    # Store
    if not args.no_store:
        result = subprocess.run([sys.executable, dedupe, "store", "--results", raw_path],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"store failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        stored = json.loads(result.stdout)
        print(f"stored {len(stored['added'])} new entries", file=sys.stderr)

    print(json.dumps({
        "date": args.date,
        "searches": len(searches),
        "raw": len(all_jobs),
        "new": len(stats["selected"]),
        "failures": failures,
        "report": os.path.join(args.out_dir, f"{args.date}_ofertas.html"),
    }, indent=2))


if __name__ == "__main__":
    main()
