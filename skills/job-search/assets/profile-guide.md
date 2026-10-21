# Building your profile

`profile.json` is the only file you need to edit. It decides **what gets searched**,
**what gets kept**, and **what gets ranked first**. Nothing about the role, country, or
seniority is hardcoded in the skill.

Read this once before your first run, and again after your first week of marks.

---

## The mental model

The scorer asks four questions about every posting, in this order:

```
1. Is this the wrong discipline?     -> stack.reject        -> drop
2. Is this below my level?           -> seniority.below    -> drop
3. Is this above my level?           -> seniority.above    -> demote to medium
4. Which of my target roles is it?   -> roles.*            -> high / medium
```

Then a second pass decides **where** it belongs:

```
location.home       -> first group  (the ones you can actually take)
location.region     -> second group (remote, still realistic)
location.out_of_scope -> dropped
```

Two rules make the whole thing behave, and both surprise people:

- **Reject wins over accept.** A title matching both a reject term and a target role is
  dropped. That ordering is deliberate: `Machine Learning Engineer` must not be rescued
  by the word `engineer`.
- **Above-level demotes, it does not drop.** A `Staff` role is still worth reading; it
  just should not sit next to a genuine mid-level match.

---

## Filling it in

### 1. `roles` — what you want to be called

Do not copy job titles you have held. Copy the **titles of the roles you want next**,
then add the synonyms other markets use for the same work.

```
roles.high     the role you are already excellent at
roles.medium   adjacent roles you could do with a short ramp-up
roles.specialist   an extra high-signal family — one that is growing and where
                   you have real evidence
```

Write them as **lowercase fragments**, not full titles. `frontend` matches
`Senior Frontend Engineer`, `Frontend Developer`, and `Frontend-разработчик`.
`Senior Frontend Engineer` matches almost nothing.

A good `roles.high` list has five to fifteen entries. Fewer and you miss postings
written by recruiters who word the title differently; more and it stops meaning anything.

### 2. `stack` — what you are not

This list does most of the work. It is the difference between 200 results you must read
and 40 you can skim.

```
stack.reject           disciplines whose core is not yours
stack.reject_unless    a discipline that is fine only when paired with something
```

`reject_unless` handles the hybrid case. If you build data backends, `backend` alone is a
no but `backend data` is a yes:

```json
"reject_unless": { "backend": ["data", "pipeline", "platform"] }
```

Include the obvious wrong languages, but also the wrong **job families**: sales
engineers, support, QA, DevOps, and — on general job boards — the industrial meanings of
your words. `programador cnc` is a real result on a real Argentine board.

### 3. `seniority` — where you sit

```
seniority.below   junior, trainee, intern, new grad, entry-level, working student
seniority.above   staff, principal, architect, head of, director, VP
```

Calibrate honestly. Three years of experience is not `staff`. Zero years should not list
`senior` as a target, and five years should not be filtering out `senior` roles because
the word intimidated them once.

Everything in `below` is dropped — entry-level roles waste a senior candidate's time.
Everything in `above` is demoted to medium, because scope can still be interesting.

### 4. `location` — where you can actually work

This is the group that most determines whether the report is useful.

```
location.home          cities, regions, and country names you can commute to
location.region        remote, or places you would relocate for
location.out_of_scope  everywhere else
```

Use **the spellings that appear in postings**, and include both the local language and
English: `munich` and `münchen`, `lisbon` and `lisboa`. Accents are folded, so you do not
need both accented and unaccented forms — but you do need both languages.

Be generous in `home`, strict in `out_of_scope`. A posting with no location text lands in
a separate "unknown" group rather than being silently dropped, because unknown is not the
same as "elsewhere".

### 5. `search` — what actually gets queried

`search.role_gate` is a cheap title pre-filter applied before scoring. It exists because
portals match loosely: a bare `desarrollador` on a general board returns sales reps and
CNC operators. The gate cannot be too narrow or you lose recall, and cannot be too wide
or you drown.

`search.searches` is the real search plan: one entry per query per portal.

```json
{ "source": "computrabajo", "query": "react", "location": "Rosario" }
{ "source": "linkedin", "query": "data engineer", "location": "Berlin, Germany" }
{ "source": "freehire", "query": "title:react OR title:frontend", "region": "eu" }
```

Rules of thumb:

- **Run broad and narrow together.** On Argentine boards, `frontend` returned 1 result
  while `desarrollador` returned 18 and `programador` 17. The local market does not use
  the English word.
- **Local language first, English second.** A German board will have `Entwickler`; a
  Spanish one will have `desarrollador`.
- **Cover each location group.** One search per city in `location.home`, plus one remote
  search.
- Twenty to thirty searches is a healthy plan. Fewer under-covers; more burns time for
  marginal gain.

### 6. `blocked_domains` — where not to bother

List hosts whose postings you cannot act on without paying. Known ones:

```json
"blocked_domains": {
  "jobleads.com": "Paywalled: applying requires a paid subscription.",
  "whatjobs.com": "JobLeads partner aggregator; most listings redirect to their paywall."
}
```

Blocked postings are removed from the main list, then listed separately with their title
and company, plus two working search links that find the same vacancy elsewhere.

---

## Three worked examples

### Frontend engineer, Argentina, 5 years

```json
"roles": { "high": ["frontend", "ui developer", "product engineer", "react developer"],
           "medium": ["developer", "desarrollador", "full stack"],
           "specialist": ["ai engineer", "llm", "agentic"] },
"seniority": { "below": ["junior", "trainee", "new grad"],
               "above": ["staff", "principal", "architect", "head of"] },
"location": { "home": ["rosario", "cordoba", "buenos aires", "argentina"],
              "region": ["remote", "chile", "uruguay", "colombia"],
              "out_of_scope": ["united states", "india", "poland"] },
"search": { "jobage": 7, "searches": [
  { "source": "computrabajo", "query": "desarrollador", "location": "Rosario" },
  { "source": "linkedin",    "query": "react developer", "location": "Argentina" },
  { "source": "freehire",    "query": "title:frontend", "region": "latam" }
]}
```

### Data engineer, Germany, 4 years

```json
"roles": { "high": ["data engineer", "analytics engineer", "etl developer"],
           "medium": ["engineer", "entwickler", "analyst"],
           "specialist": ["llm", "rag", "vector database"] },
"seniority": { "below": ["junior", "werkstudent", "praktikant", "graduate"],
               "above": ["staff", "principal", "architect", "head of"] },
"location": { "home": ["berlin", "potsdam", "germany", "deutschland"],
              "region": ["remote", "eu", "netherlands", "austria"],
              "out_of_scope": ["united states", "india", "brazil"] },
"search": { "jobage": 14, "searches": [
  { "source": "linkedin", "query": "data engineer", "location": "Berlin, Germany" },
  { "source": "linkedin", "query": "dateningenieur", "location": "Deutschland" },
  { "source": "freehire", "query": "title:data engineer", "region": "eu" }
]}
```

### Designer, fully remote, open to timezones

```json
"roles": { "high": ["product designer", "ui designer", "design engineer"],
           "medium": ["ux designer", "designer", "product design"],
           "specialist": ["design systems"] },
"seniority": { "below": ["junior", "intern", "entry level"],
               "above": ["head of design", "director", "vp"] },
"location": { "home": ["remote"],
              "region": ["europe", "latam", "americas"],
              "out_of_scope": ["hybrid", "on-site", "onsite"] },
"search": { "jobage": 7, "searches": [
  { "source": "linkedin", "query": "product designer", "location": "Remote" },
  { "source": "remoteok", "query": "design" },
  { "source": "freehire", "query": "title:designer", "region": "global" }
]}
```

Note the last one: for a fully remote search, `out_of_scope` holds **work modes**, not
places. The vocabulary is yours; the scorer only matches strings.

---

## Tuning after the first week

The first report is always wrong. That is expected — it is a starting point, not a
verdict. Work in this order:

1. **Mark everything.** Applied and out-of-scope, with reasons. Unmarked rows are counted
   as pending, and pending is not a signal.
2. **Run `feedback.py summary --days 30`.** If one reason dominates, the profile is
   wrong, not the market. Sixty percent `seniority_high` means either your target roles
   are aspirational or your CV is not selling your level.
3. **Fix the profile before adding rules.** Editing `roles` or `seniority` is
   deterministic and reversible. A learned rule is a statistical guess.
4. **Then `feedback.py learn`.** Three or more rejections of the same word, zero
   applications, becomes a demotion. It never deletes, so a mistake costs one row of
   prominence, not a lost opportunity.
5. **Re-read the reject list.** The most common miss is a job family you forgot: support
   engineer, solutions architect, technical writer. If a category keeps appearing in your
   rejects, add one fragment.

### Sanity checks

| Symptom | Likely cause |
|---|---|
| Almost nothing in the report | `roles` too narrow, or `location.home` uses spellings postings do not use |
| Hundreds of irrelevant rows | `stack.reject` missing an entire job family |
| All the good roles are demoted | `seniority.above` too broad — `senior` does not belong there |
| The same company appears five times | Expected: five distinct postings. Deduplication is by URL and by company+title |
| Nothing from one portal | Check `tools/run.py` output for a failing source; it reports rather than hides |

### What not to do

- Do not widen `jobage` to make the report look bigger. A 30-day window on a fast market
  is a week of dead listings.
- Do not put full job titles in `roles`. Fragments match; titles do not.
- Do not tune the profile against a single posting you liked. One data point is an
  anecdote.
- Do not edit `state/` by hand. `seen_jobs.json` is what makes "no repeats" true.
