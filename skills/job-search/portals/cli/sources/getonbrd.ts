import { ISO_DATE, type Job, type SearchParams, type Source } from "../types.ts";

const ENDPOINT = "https://www.getonbrd.com/api/v0/search/jobs";

type Ref = { data?: { id?: string | number; attributes?: Record<string, unknown> } | null };
type RawJob = {
  id: string;
  attributes: {
    title?: string;
    company?: Ref;
    countries?: string[];
    location_cities?: Ref;
    location_regions?: Ref;
    location_tenants?: Ref;
    remote?: boolean;
    remote_modality?: string;
    published_at?: number;
    category_name?: string;
  };
};

function place(a: RawJob["attributes"]): string | null {
  // Location refs come back as bare numeric ids with no expandable name
  // (`/api/v0/location_cities` is 404), so a numeric id tells us nothing and is
  // dropped rather than printed as "1, Chile".
  const names: string[] = [];
  for (const key of ["location_cities", "location_regions", "location_tenants"] as const) {
    const items = a[key]?.data;
    if (Array.isArray(items)) {
      for (const item of items) {
        const raw = item?.attributes?.name ?? item?.id;
        const name = raw === undefined || raw === null ? null : String(raw);
        if (name && !/^\d+$/.test(name)) names.push(name);
      }
    }
  }
  const countries = (a.countries ?? []).filter(Boolean);
  if (names.length) return `${names.join(", ")}${countries.length ? `, ${countries.join(", ")}` : ""}`;
  return countries.length ? countries.join(", ") : null;
}

export const getonbrd: Source = {
  name: "getonbrd",
  host: "getonbrd.com",

  async search(params: SearchParams): Promise<Job[]> {
    const url = new URL(ENDPOINT);
    url.searchParams.set("query", params.query);
    url.searchParams.set("per_page", String(Math.min(params.limit * 3, 50)));
    url.searchParams.append("expand[]", "company");

    const response = await fetch(url, {
      headers: { accept: "application/json", "user-agent": "job-search-skill/1.0" },
      signal: AbortSignal.timeout(25_000),
    });
    if (!response.ok) {
      throw new Error(`getonbrd responded ${response.status}`);
    }

    const payload = (await response.json()) as { data?: RawJob[] };
    const cutoff = Date.now() - params.jobage * 86_400_000;
    const jobs: Job[] = [];

    for (const raw of payload.data ?? []) {
      const a = raw.attributes ?? {};
      const published = a.published_at ? a.published_at * 1000 : null;
      if (published && published < cutoff) continue;

      const companyRef = a.company?.data;
      const company =
        (companyRef?.attributes?.name as string | undefined) ??
        (companyRef?.id ? String(companyRef.id) : null);

      jobs.push({
        id: raw.id,
        title: a.title ?? "(untitled)",
        company,
        location: place(a),
        date: published ? ISO_DATE(new Date(published)) : null,
        url: `https://www.getonbrd.com/jobs/${raw.id}`,
        portal: "getonbrd",
        modality: a.remote_modality ?? (a.remote ? "remote" : null),
      });
    }

    return jobs.slice(0, params.limit);
  },
};
