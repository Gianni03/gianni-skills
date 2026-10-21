import { readFileSync } from "node:fs";
import { ISO_DATE, type Job, type SearchParams, type Source } from "../types.ts";

/**
 * Reads public Telegram channels through the server-rendered web preview at
 * https://t.me/s/<handle>. That page needs no login, no bot token, and no API
 * key, and it carries the last ~20 posts of the channel.
 *
 * It does NOT work for private channels (invite links of the form t.me/+...):
 * those have no public preview. Reading them needs a logged-in MTProto client.
 *
 * Channels are listed one handle per line in state/telegram_channels.txt;
 * blank lines and # comments are ignored.
 *
 * The stack gate and the place list come from profile.json
 * (`sources.telegram.stack_terms` and `sources.telegram.places`) so the skill is
 * not tied to one candidate's field. Without a profile, a permissive default
 * keeps the source usable instead of returning nothing.
 */

const CHANNELS_FILE = new URL("../../../state/telegram_channels.txt", import.meta.url).pathname;
const PROFILE_FILE = new URL("../../../profile.json", import.meta.url).pathname;

type TelegramConfig = { stack_terms?: string[]; places?: string[] };

function loadTelegramConfig(): TelegramConfig {
  try {
    const profile = JSON.parse(readFileSync(PROFILE_FILE, "utf-8"));
    return profile?.sources?.telegram ?? {};
  } catch {
    return {};
  }
}

const CONFIG = loadTelegramConfig();

/** A post must name something the candidate actually works with. */
const STACK_TERMS = (CONFIG.stack_terms ?? []).map((term) => term.toLowerCase());

const PLACES = CONFIG.places ?? [];

function loadChannels(): string[] {
  try {
    return readFileSync(CHANNELS_FILE, "utf-8")
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#"))
      .map((line) =>
        line
          .replace(/^https?:\/\/(www\.)?t\.me\/(s\/)?/, "")
          .replace(/\/.*$/, "")
          .replace(/^@/, ""),
      );
  } catch {
    return [];
  }
}

function decode(html: string): string {
  return html
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]*>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number(dec)))
    .replace(/&amp;/g, "&")
    .trim();
}

type Post = { id: string; date: string | null; text: string };

async function fetchChannel(handle: string): Promise<Post[]> {
  const response = await fetch(`https://t.me/s/${handle}`, {
    headers: {
      "user-agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
      accept: "text/html",
    },
    signal: AbortSignal.timeout(25_000),
  });
  if (!response.ok) throw new Error(`t.me/s/${handle} responded ${response.status}`);

  const html = await response.text();
  const chunks = html.split('data-post="').slice(1);

  // t.me answers 200 with an empty preview when it rate-limits. Treating that
  // as "channel has no posts" silently loses the whole source, so it is raised
  // as a failure the caller can report.
  if (!chunks.length && !/tgme_widget_message/i.test(html)) {
    throw new Error(`t.me/s/${handle} returned no posts (rate limited or preview disabled)`);
  }

  const posts: Post[] = [];

  for (const chunk of chunks) {
    const postId = chunk.match(/^([^"]+)"/)?.[1] ?? null;
    if (!postId) continue;

    const time = chunk.match(/<time[^>]*datetime="([^"]+)"/)?.[1] ?? null;
    const body = chunk.match(/class="tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)<\/div>/)?.[1];
    if (!body) continue;

    const text = decode(body);
    if (text) posts.push({ id: postId, date: time ? ISO_DATE(new Date(time)) : null, text });
  }

  return posts;
}

export const telegram: Source = {
  name: "telegram",
  host: "t.me",

  async search(params: SearchParams): Promise<Job[]> {
    const channels = loadChannels();
    if (!channels.length) {
      throw new Error(
        `no channels configured — add one public handle per line to ${CHANNELS_FILE}`,
      );
    }

    const settled = await Promise.allSettled(channels.map(fetchChannel));
    const cutoff = Date.now() - params.jobage * 86_400_000;
    const terms = params.query.toLowerCase().split(/\s+/).filter(Boolean);
    const jobs: Job[] = [];
    const failures: string[] = [];

    settled.forEach((result, index) => {
      if (result.status === "rejected") {
        failures.push(`${channels[index]}: ${(result.reason as Error)?.message ?? result.reason}`);
        return;
      }

      for (const post of result.value) {
        const lower = post.text.toLowerCase();

        // Technology gate: the post must name something the candidate works with.
        // An empty list disables the gate rather than dropping everything.
        if (STACK_TERMS.length && !STACK_TERMS.some((term) => lower.includes(term))) continue;

        // Query gate: every query word must appear somewhere in the post, so the
        // body counts and not just the headline.
        if (terms.length && !terms.every((term) => lower.includes(term))) continue;

        if (post.date && new Date(post.date).getTime() < cutoff) continue;

        const firstLine =
          post.text.split("\n").map((line) => line.trim()).find((line) => line.length > 0) ??
          "(sin título)";
        const place = PLACES.find((p) => post.text.includes(p)) ?? null;

        jobs.push({
          id: post.id,
          title: firstLine.slice(0, 140),
          company: null,
          location: place,
          date: post.date,
          url: `https://t.me/${post.id}`,
          portal: `telegram:${channels[index]}`,
          modality: /\bremoto|remote\b/i.test(post.text)
            ? "remote"
            : /\bh[ií]brido|hybrid\b/i.test(post.text)
              ? "hybrid"
              : null,
        });
      }
    });

    if (failures.length && !jobs.length) {
      throw new Error(failures.join("; "));
    }
    jobs.sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
    return jobs.slice(0, params.limit);
  },
};
