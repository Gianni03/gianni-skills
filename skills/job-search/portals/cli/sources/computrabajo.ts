import { ISO_DATE, type Job, type SearchParams, type Source } from "../types.ts";

const BASE = "https://ar.computrabajo.com";

function slug(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function stripTags(html: string): string {
  return html
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number(dec)))
    .replace(/\s+/g, " ")
    .trim();
}

/** "Hace 2 días" / "Hoy" / "Ayer" / "Hace 3 horas" -> ISO date. */
function parseRelativeDate(text: string): string | null {
  const value = text.toLowerCase();
  const today = new Date();
  if (value.includes("hoy") || value.includes("today")) return ISO_DATE(today);
  if (value.includes("ayer")) {
    return ISO_DATE(new Date(today.getTime() - 86_400_000));
  }
  const match = value.match(/hace\s+(\d+)\s*(minuto|hora|d[ií]a|semana|mes|año)/);
  if (!match) return null;
  const amount = Number(match[1]);
  const unit = match[2];
  const days =
    unit.startsWith("minuto") ? 0
    : unit.startsWith("hora") ? 0
    : unit.startsWith("d") ? amount
    : unit.startsWith("semana") ? amount * 7
    : unit.startsWith("mes") ? amount * 30
    : amount * 365;
  return ISO_DATE(new Date(today.getTime() - days * 86_400_000));
}

function firstMatch(block: string, pattern: RegExp): string | null {
  const match = block.match(pattern);
  return match ? stripTags(match[1]) : null;
}

export const computrabajo: Source = {
  name: "computrabajo",
  host: "ar.computrabajo.com",

  async search(params: SearchParams): Promise<Job[]> {
    const path = params.location
      ? `/trabajo-de-${slug(params.query)}-en-${slug(params.location)}`
      : `/trabajo-de-${slug(params.query)}`;

    const response = await fetch(`${BASE}${path}`, {
      headers: {
        "user-agent":
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
        accept: "text/html,application/xhtml+xml",
        "accept-language": "es-AR,es;q=0.9",
      },
      signal: AbortSignal.timeout(25_000),
    });
    if (!response.ok) {
      throw new Error(`computrabajo responded ${response.status}`);
    }

    const html = await response.text();
    const blocks = html.split(/<article\b/i).slice(1);
    const cutoff = Date.now() - params.jobage * 86_400_000;
    const jobs: Job[] = [];

    for (const block of blocks) {
      if (!/box_offer/i.test(block.slice(0, 400))) continue;

      const id = block.match(/data-id=['"]([^'"]+)['"]/)?.[1] ?? null;
      const href = block.match(/class="js-o-link[^"]*"\s+href="([^"]+)"/)?.[1] ?? null;
      const title = firstMatch(block, /class="js-o-link[^"]*"[^>]*>([\s\S]*?)<\/a>/);
      if (!id || !href || !title) continue;

      const company = firstMatch(block, /offer-grid-article-company-url[^>]*>([\s\S]*?)<\/a>/);
      const location = firstMatch(block, /class="fs16 fc_base mt5"[^>]*>\s*<span class="mr10">([\s\S]*?)<\/span>/);
      const modality = firstMatch(block, /i_home_office"><\/span>\s*([\s\S]*?)<\/span>/);
      const date = parseRelativeDate(firstMatch(block, /class="fs13 fc_aux mt15"[^>]*>([\s\S]*?)<\/p>/) ?? "");
      if (date && new Date(date).getTime() < cutoff) continue;

      jobs.push({
        id,
        title,
        company,
        location,
        date,
        url: href.startsWith("http") ? href.replace(/#.*$/, "") : `${BASE}${href.replace(/#.*$/, "")}`,
        portal: "computrabajo",
        modality,
      });

      if (jobs.length >= params.limit) break;
    }

    return jobs;
  },
};
