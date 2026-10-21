#!/usr/bin/env bun
/**
 * Multi-portal job search CLI.
 *
 *   portals search -q "frontend" [-s getonbrd,computrabajo] [-l "<city>"]
 *                  [--jobage 14] [-n 20] [-f json|table]
 *   portals list
 *
 * Every source returns the same Job shape, so results merge without special cases.
 * A source that throws is reported and skipped; it never aborts the run.
 */
import type { Job, Source } from "./types.ts";
import { getonbrd } from "./sources/getonbrd.ts";
import { computrabajo } from "./sources/computrabajo.ts";
import { remoteok } from "./sources/remoteok.ts";
import { telegram } from "./sources/telegram.ts";

const SOURCES: Source[] = [getonbrd, computrabajo, remoteok, telegram];

const fold = (value: string): string =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

/**
 * Role gate. Portals match loosely — computrabajo returns sales reps and CNC
 * operators for "desarrollador" — so the title must name one of the wanted
 * roles. Comma-separated, any-of semantics.
 */
function applyRoles(jobs: Job[], roles: string[]): Job[] {
  if (!roles.length) return jobs;
  const needed = roles.map(fold);
  return jobs.filter((job) => {
    const title = fold(job.title ?? "");
    return needed.some((role) => title.includes(role));
  });
}

/**
 * Only computrabajo filters by place server-side. For the other sources the
 * location is applied here: a job whose own location text does not mention the
 * requested place is dropped. A job with no location text at all is kept —
 * unknown is not the same as "somewhere else".
 */
function applyLocation(jobs: Job[], location?: string): Job[] {
  if (!location) return jobs;
  const needle = fold(location);
  return jobs.filter((job) => {
    if (!job.location) return true;
    return fold(job.location).includes(needle);
  });
}

type Args = {
  command: "search" | "list";
  sources: string[];
  query: string;
  location?: string;
  jobage: number;
  limit: number;
  roles: string[];
  format: "json" | "table";
};

function parseArgs(argv: string[]): Args {
  const args: Args = {
    command: "search",
    sources: [],
    query: "",
    jobage: 7,
    limit: 20,
    roles: [],
    format: "json",
  };

  const rest = [...argv];
  if (rest[0] === "list") {
    args.command = "list";
    return args;
  }
  if (rest[0] === "search") rest.shift();

  const take = (i: number, flag: string): string => {
    const value = rest[i + 1];
    if (value === undefined || value.startsWith("--")) {
      throw new Error(`missing value for ${flag}`);
    }
    return value;
  };

  for (let i = 0; i < rest.length; i++) {
    const arg = rest[i];
    switch (arg) {
      case "-q":
      case "--query":
        args.query = take(i, arg);
        i++;
        break;
      case "-l":
      case "--location":
        args.location = take(i, arg);
        i++;
        break;
      case "-s":
      case "--source":
        args.sources.push(...take(i, arg).split(",").map((s) => s.trim()).filter(Boolean));
        i++;
        break;
      case "--jobage":
        args.jobage = Number(take(i, arg));
        i++;
        break;
      case "-n":
      case "--limit":
        args.limit = Number(take(i, arg));
        i++;
        break;
      case "-r":
      case "--role":
        args.roles.push(...take(i, arg).split(",").map((r) => r.trim()).filter(Boolean));
        i++;
        break;
      case "-f":
      case "--format": {
        const value = take(i, arg);
        if (value !== "json" && value !== "table") {
          throw new Error(`unknown format: ${value}`);
        }
        args.format = value;
        i++;
        break;
      }
      default:
        if (arg.startsWith("-")) throw new Error(`unknown flag: ${arg}`);
    }
  }

  if (!args.query) throw new Error("--query is required");
  if (!Number.isFinite(args.jobage) || args.jobage <= 0) throw new Error("--jobage must be a positive number");
  if (!Number.isFinite(args.limit) || args.limit <= 0) throw new Error("--limit must be a positive number");
  return args;
}

function selected(args: Args): Source[] {
  if (!args.sources.length || args.sources.includes("all")) return SOURCES;
  const wanted = new Set(args.sources);
  const unknown = [...wanted].filter((name) => !SOURCES.some((s) => s.name === name));
  if (unknown.length) {
    throw new Error(`unknown source(s): ${unknown.join(", ")}. Available: ${SOURCES.map((s) => s.name).join(", ")}`);
  }
  return SOURCES.filter((s) => wanted.has(s.name));
}

function renderTable(jobs: Job[]): string {
  const header = ["PORTAL", "DATE", "TITLE", "COMPANY", "LOCATION"];
  const rows = jobs.map((j) => [
    j.portal,
    j.date ?? "-",
    (j.title ?? "").slice(0, 46),
    (j.company ?? "-").slice(0, 24),
    (j.location ?? "-").slice(0, 34),
  ]);
  const widths = header.map((h, i) =>
    Math.max(h.length, ...rows.map((r) => (r[i] ?? "").length), 4),
  );
  const line = (cells: string[]) => cells.map((c, i) => c.padEnd(widths[i])).join("  ");
  return [line(header), widths.map((w) => "-".repeat(w)).join("  "), ...rows.map(line)].join("\n");
}

async function main(): Promise<void> {
  let args: Args;
  try {
    args = parseArgs(Bun.argv.slice(2));
  } catch (error) {
    console.error(JSON.stringify({ error: (error as Error).message, code: "BAD_ARG" }));
    process.exit(1);
  }

  if (args.command === "list") {
    console.log(
      JSON.stringify(
        SOURCES.map((s) => ({ name: s.name, host: s.host })),
        null,
        2,
      ),
    );
    return;
  }

  const targets = selected(args);
  const settled = await Promise.allSettled(
    targets.map((source) =>
      source.search({
        query: args.query,
        location: args.location,
        jobage: args.jobage,
        limit: args.limit,
      }),
    ),
  );

  const collected: Job[] = [];
  const errors: { portal: string; error: string }[] = [];
  settled.forEach((result, index) => {
    const portal = targets[index].name;
    if (result.status === "fulfilled") {
      collected.push(...result.value);
    } else {
      errors.push({ portal, error: (result.reason as Error)?.message ?? String(result.reason) });
    }
  });

  const jobs = applyRoles(applyLocation(collected, args.location), args.roles);
  jobs.sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));

  if (args.format === "table") {
    if (jobs.length) console.log(renderTable(jobs));
    else console.log("(no results)");
    for (const e of errors) console.error(`warning: ${e.portal} failed: ${e.error}`);
    return;
  }

  console.log(
    JSON.stringify(
      {
        meta: { count: jobs.length, query: args.query, location: args.location ?? null, jobage: args.jobage },
        results: jobs,
        errors,
      },
      null,
      2,
    ),
  );
}

await main();
