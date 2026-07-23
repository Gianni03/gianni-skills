# Mock Interview Rubric

Scoring grid and drill mechanics for the `mock-interview` mode. Built on Meta's 5 behavioral focus areas (`assets/pdfs/metainterview.pdf`) as the scoring skeleton, with STAR / Nugget-First as the answer-structure requirement.

## Session flow

```
GREETING → PERSONALITY + MOOD CAPTURE → WARMUP (1 question) → DRILL ROUNDS (5–8 questions) → TRAP ROUND (1 question) → CANDIDATE QUESTIONS ROUND → SCORECARD + FEEDBACK
```

1. **Greeting**: confirm the user wants a mock interview now. Ask which JD (paste, file path, or "skip — general rehearsal"). If the user already ran `playbook` for the same JD in this session, prefer to reuse that playbook as the question source.
2. **Personality + mood capture**: read the user's primary style from the session (if `personality-strategy` was run earlier) OR walk the "Which line lands?" diagnostic in `personality-cheatsheet.md`. Then ask for today's mood: motivated / eager / cautious / discouraged / defensive / neutral. Apply the mood overlay.
3. **Warmup**: one A-family question (the elevator pitch). This is low-stakes — the point is to get the user talking. Do NOT score it; only give one short feedback note ("you landed the nugget — good" or "your opening was a CV recital; re-pitch in 30 seconds using the nugget-first technique").
4. **Drill rounds**: 5 to 8 questions drawn from B/C/D/E families based on the JD (when available) or on a balanced rotation (when no JD). One question at a time, wait for the answer, score, brief inline feedback, next question.
5. **Trap round**: exactly one trap or difficult question from `question-bank.md` section B or E. Score it harshly on the "what NOT to do" criterion.
6. **Candidate questions round**: ask the user to produce 3 questions THEY would ask the interviewer. Score each: genuine vs insightful vs passion mix; specificity to the company; whether it would actually help the user decide if they want the job.
7. **Scorecard + feedback**: aggregate the per-focus-area scores, surface the 3 weakest items with concrete re-drill suggestions, and end the session.

## The 5 focus areas (scoring dimensions)

Every drill answer is scored 0–3 against each of the 5 areas. Track across the session.

| Focus area | 0 — absent | 1 — weak | 2 — solid | 3 — strong |
|---|---|---|---|---|
| Resolving conflict | No conflict element; answer avoids the topic entirely. | Conflict mentioned but resolution vague or credited to others ("we"). | Conflict described + user's specific role + resolution reached. | Conflict described + user's role + resolution + measurable outcome + lesson. |
| Growing continuously | No learning signal; treats the situation as static. | Mentions learning but vague ("I learned a lot"). | Names one specific skill/insight gained AND how it was applied later. | Names the skill + how it was applied + the measurable impact of the new skill. |
| Embracing ambiguity | Freezes; asks the interviewer for clarification instead of answering. | Acknowledges ambiguity but doesn't demonstrate decision-making under it. | Makes an explicit assumption, proceeds, and flags the assumption. | Makes the assumption, proceeds, flags it, AND adjusts course when new info appears in the drill. |
| Driving results | No result; action without outcome. | Result stated but unquantified ("it worked"). | Result quantified (e.g. "cut 40% latency"). | Result quantified + tied to user's specific contribution ("I drove X, which caused Y"). |
| Communicating effectively | Answer incoherent or extreme over-detail. | Coherent but too long/short; lacks structure. | Nuggets-first + STAR structurally followed. | Nuggets-first + STAR + tailored to the question + concise. |

## Trap question scoring (additional criterion)

Trap answers are scored on the 5 focus areas AND on a 6th dimension specific to traps:

| Trap criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Avoided the trap | Fell into it (negativity, dishonesty, or desperation leaked). | Avoided it technically but came across evasive. | Avoided it cleanly but generic. | Reframed it into a substantive answer that advanced their candidacy. |

## Answer-structure requirement (orthogonal to scoring)

Every behavioral answer (C-family) is expected to follow Nugget-First + STAR:

1. Nugget: one-line gist delivered first
2. Situation
3. Task (or fold into Situation per Cracking's S.A.R.)
4. Action (uses "I", not "we"; specific)
5. Result (quantified when possible; include a learning when relevant)

If the answer skips the nugget or skips the result, that's an automatic -1 on "Communicating effectively" for the round, regardless of content quality. Surface this in feedback explicitly.

## Feedback mechanics

- **Inline (after each answer)**: 1–2 sentences max. One thing that worked, one thing to improve. Do NOT coach exhaustively mid-session — it breaks role-play.
- **Final scorecard**: per-focus-area average across the session, the 3 weakest items with concrete re-drill suggestions, the trap-question verdict, and a single overall readiness verdict:
  - **Ready** — all focus area averages ≥ 2.0, no 0s.
  - **Almost ready** — one focus area at 1.5 OR one trap failure.
  - **Not ready yet** — any focus area average < 1.5 OR two trap failures OR zero on "Communicating effectively" twice.

The readiness verdict is final and uses the same language regardless of style; the coaching below it is personality-aware (use the style's advice-to-self line as the coaching voice).

## Output contract

The `mock-interview` mode does NOT save a file by default — it's a live session. If the user asks for the session to be persisted, save the final scorecard to `output/mock-scorecard_<date>.md`. Reporting inline is the default.