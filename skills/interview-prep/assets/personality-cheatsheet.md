# Personality Cheatsheet — The Four Interview Styles

Self-identification heuristic and per-archetype coaching tables. The user identifies their primary style by reading the four profiles and answering the "Which line lands?" diagnostic. The mood overlay is applied on top.

## How to self-identify (for the skill's `personality-strategy` mode)

Present the user the four "Which line lands?" sentences and let them pick the one that most feels like them IN INTERVIEWS (not in life in general):

- "I want to be liked." → Charmer
- "I want to be heard." → Challenger
- "I want to get it right." → Examiner
- "I want to fit in." → Harmonizer

If the user hedges between two, the secondary is their neighbor-tendency (results in a hybrid like Charmer/Challenger). Never force a single label if the user feels split.

## Quick axis check (use when the four-line diagnostic is ambiguous)

- **Energy axis**: After a long interview, do you feel drained by talking or energized by it? Drained → Introvert side (Examiner / Harmonizer). Energized → Extrovert side (Charmer / Challenger).
- **Orientation axis**: In the interview, do you unconsciously adjust to what the interviewer seems to want (Accommodating: Charmer / Harmonizer), or do you hold your line even when it gets uncomfortable (Steadfast: Challenger / Examiner)?

## The Charmer (extroverted + accommodating)

| Field | Value |
|---|---|
| Priority line | "I want to be liked." |
| Show-value line | Shows value by being eager — visible enthusiasm, willingness, energy. |
| Interview-as metaphor | A performance — the interviewer is the audience. |
| At-worst verb | Coerces — enthusiasm curdles into pressure on the interviewer to like them back. |
| Advice-to-self | Curb the eagerness; let one piece of substance land before the next flourish. One deep answer beats three shallow ones. |
| Focus | Externally focused on the interviewer's reactions. |
| Time orientation | Past → future oriented (the trajectory they're selling). |
| Drawn-to | The Examiner — they ground the Charmer and seem substantive by contrast. |
| Opposite style | The Examiner. |
| Trap | Overrehearsing charm and forgetting to demonstrate competence; talking too much. |
| Best opening | A 30-second nugget that demonstrates competence FIRST, then warms up. |

## The Challenger (extroverted + steadfast)

| Field | Value |
|---|---|
| Priority line | "I want to be heard." |
| Show-value line | Shows value by questioning — they have opinions and they voice them. |
| Interview-as metaphor | A cross-examination — interviewer is an investigator. |
| At-worst verb | Demands — opinionatedness curdles into challenging the interviewer's competence. |
| Advice-to-self | Ask one sharper question per round, not three. Make room for the interviewer's authority; defer on territory, question on substance. |
| Focus | Internally focused on what THEY think. |
| Time orientation | Past → future oriented. |
| Drawn-to | The Harmonizer — softens them, makes them listen. |
| Opposite style | The Harmonizer. |
| Trap | Coming across as confrontational or as a know-it-all; making the interviewer feel small. |
| Best opening | Lead with genuine curiosity about the team's current bet, THEN position your viewpoint as a build. |

## The Examiner (introverted + steadfast)

| Field | Value |
|---|---|
| Priority line | "I want to get it right." |
| Show-value line | Shows value by being precise — they take the question literally and answer it rigorously. |
| Interview-as metaphor | A graded test — the interviewer is an examiner. |
| At-worst verb | Withholds — in the name of accuracy they answer too narrowly and never let personality through. |
| Advice-to-self | Add a half-sentence of warmth per answer; don't make the interviewer pull it out of you. Share one personal detail outside the literal question. |
| Focus | Internally focused on what THEY know. |
| Time orientation | Present oriented. |
| Drawn-to | The Charmer — warms them up, lowers the stakes. |
| Opposite style | The Charmer. |
| Trap | Sounding cold or evasive; refusing to show enthusiasm even when they feel it. |
| Best opening | Answer the question precisely AND add one line of why-this-company-matters-to-you. |

## The Harmonizer (introverted + accommodating)

| Field | Value |
|---|---|
| Priority line | "I want to fit in." |
| Show-value line | Shows value by being agreeable — cooperative, easy to work with, adaptable. |
| Interview-as metaphor | A team tryout — interviewer is a future teammate. |
| At-worst verb | Downplays — agreeableness curdles into minimizing their own contribution. |
| Advice-to-self | Use "I" relentlessly in STAR answers; you are allowed to be the protagonist of your own story. Claim one achievement per round without softening. |
| Focus | Externally focused on fitting the interviewer's expectations. |
| Time orientation | Present oriented. |
| Drawn-to | The Challenger — models agency for them. |
| Opposite style | The Challenger. |
| Trap | Downplaying own achievements; "we did X" instead of "I did X". |
| Best opening | Use the "why this role" opening but anchor it to one of YOUR specific strengths, not to "I'm excited to learn". |

## The 12 sub-variants

Each primary style has 2 neighbor-tendency variants. Treat the variant as a lighter blend of the primary with its neighbor. The hexagon adjacency is: Charmer↔Challenger↔Examiner↔Harmonizer↔Charmer. So:

- **Charmer/Challenger** — eager AND opinionated. Curb both impulses; lead with one assertive observation, then one invitation to react.
- **Charmer/Harmonizer** — eager AND agreeable. Risk: over-pleasing. Anchor to a concrete achievement.
- **Challenger/Charmer** — questioning AND eager. Risk: charming through questions and never landing substance.
- **Challenger/Examiner** — questioning AND precise. Risk: the interviewer feels like they're being audited.
- **Examiner/Challenger** — precise AND opinionated. Risk: cold + defensive; bring warmth explicitly.
- **Examiner/Harmonizer** — precise AND agreeable. Risk: too quiet, lets the room talk over them.
- **Harmonizer/Examiner** — agreeable AND precise. Risk: precision makes them hesitate longer, makes them seem slow.
- **Harmonizer/Charmer** — agreeable AND eager. Risk: spreading warmth thin and forgetting to claim wins.

## Mood overlay mechanics

The mood overlay is a **session-time adjustment** that nudges which advice to surface and which questions to drill harder. The user declares a mood when invoking `personality-strategy`. The skill maps that mood to a neighboring-tendency push:

| Declared mood | Overlay shape | What the skill does |
|---|---|---|
| `motivated` | Lean toward the extrovert neighbor. | Surface the "best opening" advice and prioritize A-family drills. |
| `eager` | Lean toward the Charmer neighbor. | Surface the "substance FIRST, warmth second" reminder; warn about the trap. |
| `cautious` | Lean toward the Examiner neighbor. | Surface the "add warmth per answer" reminder; do an A-family warmup. |
| `discouraged` | Lean toward the Harmonizer neighbor. | Surface the "use I, not we" reminder; do an achievement-claim drill. |
| `defensive` | Lean toward the Challenger neighbor. | Surface the "one sharp question per round" reminder; do a listen-before-question drill. |
| `neutral` / not declared | No overlay. | Run on primary style alone. |

The mood never replaces the primary style; it overlays. The output strategy document labels both (e.g. "Primary: Examiner, Mood today: motivated → overlay leans Charmer tendencies; specifically, lead with enthusiasm in the opening").