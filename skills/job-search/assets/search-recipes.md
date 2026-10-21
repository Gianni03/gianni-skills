# Portal recipes

What each source actually does with a query, learned by running them. Use this when
writing `search.searches` in `profile.json`.

The worked examples below use Argentina and frontend, because that is where the quirks
were measured. The behaviour transfers; the vocabulary does not.

---

## computrabajo — city-level, loose matching

The only source here that filters by city **server-side**. The URL is built as
`trabajo-de-<role>-en-<city>`.

```
{ "source": "computrabajo", "query": "desarrollador", "location": "Rosario" }
```

Measured in Rosario, Argentina:

| Query | Results |
|---|---|
| `desarrollador` | 18 |
| `programador` | 17 |
| `full stack` | 2 |
| `react` | 2 |
| `typescript` | 2 |
| `frontend` | 1 |

The lesson generalizes: **the local market does not use the English word.** A bare
`frontend` finds almost nothing on a local board while `desarrollador` carries the
recall. Always run one broad local-language query per city.

Matching is loose in the other direction too. `desarrollador` also returns sales reps,
CNC operators, and construction leads. That is why `search.role_gate` exists.

City slugs are province-ish, not precise:

- `-l "<city>"` — precise for a major city
- `-l "<province>"` — loose: returns neighbouring cities and some capital noise
- Capital districts sometimes need their own name (`Capital Federal`) rather than the
  metro name (`Buenos Aires`), which mixes in surrounding cities

## getonbrd — LatAm tech, structured

Public JSON API, no auth. Chilean-centric, so expect Chile first and other LatAm markets
rarely. Valuable for its `modality`, `countries`, and `remote_modality` fields.

```
{ "source": "getonbrd", "query": "frontend" }
{ "source": "getonbrd", "query": "product engineer" }
```

No city filter exists. `--location` is applied client-side by substring, so it can only
work with what the posting states. Location refs in the API are bare numeric ids with no
expandable name, so city detail is often unavailable — `countries` is the reliable field.

## remoteok — remote, not tech-only

Public JSON API. The first array element is a legal/attribution notice, not a posting.

```
{ "source": "remoteok", "query": "react" }
```

It is a general remote board, so it surfaces risk analysts and support reps alongside
engineers. It also tends to be US-eligible-heavy; screen timezone and work authorization
before investing time.

If you republish results, RemoteOK's terms require attribution and a follow link back.

## freehire — facets, not free text

Structured facets, never a location string.

```
{ "source": "freehire", "query": "title:react OR title:frontend", "region": "latam" }
```

- `-q` understands `OR` (uppercase only) and a leading `title:` to restrict to titles.
  Space-separated words are an **AND**, which returns fewer jobs, not more.
- `--region`, `--country`, `--city` form one OR-group. `--region us` is invalid — `us` is
  a country code, not a region.
- Search results already carry the full description, so do not loop `detail` over hits.
- `location` can be an eligible-country list of 200+ characters. Collapse it for display.

Region codes: `global`, `eu`, `uk`, `north_america`, `latam`, `apac`, `mena`, `africa`,
`cis`. `eu` does not include the UK.

## linkedin — free text, and `Remote` is not a filter

```
{ "source": "linkedin", "query": "react developer", "location": "Berlin, Germany" }
```

City and country names work as free text. **`-l "Remote"` is not a geographic filter** —
it returns global remote postings, including cities you never asked for. Filter timezone
yourself.

`detail` returns `isActive`. `false` means the page shows "No longer accepting
applications", so the posting died between indexing and fetching. Mark it expired and
leave it out.

## telegram — public channels only

```
{ "source": "telegram", "query": "react" }
```

Channels are configured in `state/telegram_channels.txt`, one public handle per line. The
preview carries roughly the last 20 posts, so it is a freshness filter, not an archive.

The source applies two gates from `profile.json`:

- `sources.telegram.stack_terms` — the post must name one of these technologies.
  Without it, general LATAM channels fill the list with Java and .NET roles.
- `sources.telegram.places` — place names it tries to detect in the post text.

An empty `stack_terms` list disables the gate rather than dropping everything.

Private channels (`t.me/+...`) have no preview and cannot be read this way.

---

## Writing a plan

Twenty to thirty searches is a healthy plan. Cover, for each location group:

1. **Local language, broad** — the word your market uses for the role family.
2. **Local language, narrow** — the specific stack.
3. **English** — for multinationals posting in English locally.
4. **Remote** — one or two searches with no city.
5. **Specialist family** — if you have a second edge, one query for it.

A worked plan for frontend in Argentina (Rosario / Córdoba / Santa Fe / CABA):

```json
[
  { "source": "computrabajo", "query": "desarrollador", "location": "Rosario" },
  { "source": "computrabajo", "query": "react", "location": "Rosario" },
  { "source": "computrabajo", "query": "desarrollador", "location": "Cordoba" },
  { "source": "computrabajo", "query": "desarrollador", "location": "Santa Fe" },
  { "source": "computrabajo", "query": "frontend", "location": "Capital Federal" },

  { "source": "linkedin", "query": "frontend developer", "location": "Rosario, Santa Fe, Argentina" },
  { "source": "linkedin", "query": "react developer", "location": "Argentina" },
  { "source": "linkedin", "query": "AI engineer", "location": "Argentina" },

  { "source": "getonbrd", "query": "frontend" },
  { "source": "getonbrd", "query": "product engineer" },

  { "source": "freehire", "query": "title:frontend engineer OR title:react developer", "region": "latam" },
  { "source": "freehire", "query": "title:ai engineer OR title:llm", "region": "latam" },

  { "source": "remoteok", "query": "react" },
  { "source": "telegram", "query": "react" }
]
```

## Date window

Seven days by default. Three rules make "fresh and applicable" real, and all three are
enforced in code:

- A posting dated more than `jobage` days ago is dropped, even if never seen.
- A posting whose deadline already passed is dropped, even if posted yesterday.
- A posting with **no date** is excluded by default, because freshness cannot be proven.
  It is reported in an `undated` bucket rather than silently discarded.

Measured cost of tightening 14 → 7 days: a local board changed nothing (it is naturally
fresh), while the international feeds lost roughly half their volume. The lost half was
mostly dead listings.
