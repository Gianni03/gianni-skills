import { ISO_DATE, type Job, type SearchParams, type Source } from "../types.ts";

type RawJob = {
  id?: string;
  slug?: string;
  position?: string;
  company?: string;
  location?: string;
  date?: string;
  url?: string;
  tags?: string[];
  salary_min?: number;
  salary_max?: number;
};

export const remoteok: Source = {
  name: "remoteok",
  host: "remoteok.com",

  async search(params: SearchParams): Promise<Job[]> {
    const response = await fetch("https://remoteok.com/api", {
      headers: {
        "user-agent": "job-search-skill/1.0 (+personal use; links back to Remote OK)",
        accept: "application/json",
      },
      signal: AbortSignal.timeout(25_000),
    });
    if (!response.ok) {
      throw new Error(`remoteok responded ${response.status}`);
    }

    // The first element is a legal/attribution notice, not a posting.
    const payload = (await response.json()) as RawJob[];
    const cutoff = Date.now() - params.jobage * 86_400_000;
    const query = params.query.toLowerCase().split(/\s+/).filter(Boolean);
    const jobs: Job[] = [];

    for (const raw of payload) {
      if (!raw?.position || !raw?.id) continue;

      const haystack = `${raw.position} ${raw.company ?? ""} ${(raw.tags ?? []).join(" ")}`.toLowerCase();
      if (query.length && !query.every((term) => haystack.includes(term))) continue;

      const posted = raw.date ? new Date(raw.date) : null;
      if (posted && posted.getTime() < cutoff) continue;

      jobs.push({
        id: String(raw.id),
        title: raw.position,
        company: raw.company ?? null,
        location: raw.location || "Remote",
        date: posted ? ISO_DATE(posted) : null,
        url: raw.url ?? `https://remoteok.com/remote-jobs/${raw.id}`,
        portal: "remoteok",
        modality: "remote",
      });

      if (jobs.length >= params.limit) break;
    }

    return jobs;
  },
};
