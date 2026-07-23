# Mode Procedures

Detailed execution steps for each `interview-prep` mode. SKILL.md points here; this file holds the operational detail.

## `personality-strategy` mode

1. Walk the "Which line lands?" diagnostic from `assets/personality-cheatsheet.md`. If the user already declared a primary style this session, confirm it instead of re-asking.
2. Ask for today's mood via the `question` tool: motivated / eager / cautious / discouraged / defensive / neutral. Accept free-text too — map it to the closest neighbor-tendency overlay and name the at-worst risk it triggers. Never force a label.
3. Map the mood to the overlay per the personality-cheatsheet mood table. For free-text moods, combine the closest primary-neighbor overlay with the at-worst verb it triggers.
4. Generate the strategy document: primary style profile, today's overlay, best opening advice, two traps to watch for, two answer-structure reminders (Nugget First + STAR). Present inline.
5. Ask whether to proceed to `playbook` or `mock-interview`.

## `playbook` mode

1. Request the JD (paste or file path). If no JD, ask whether to run a general rehearsal or stop. Cultural-fit questions need a JD — do not fabricate without one.
2. If a JD is provided, optionally `webfetch` the company site (or reuse `job-application`'s `company-research` output).
3. Use `assets/question-bank.md` families A through E. Select from each:
   - A (self-introduction + narrative): one elevator pitch exercise + one "why this company" answer skeleton.
   - B (strengths & weaknesses): one strengths, one weakness with trap-handling coaching.
   - C (behavioral/STAR): 3–5 questions selected by JD signal keywords. Provide an answer strategy for each, NOT a fully scripted answer (the user should voice their own version).
   - D (leadership & teamwork): one question selected by JD seniority signals.
   - E (cultural-fit + trap): two E questions where one is a trap. Include "what NOT to do" coaching for the trap.
4. Generate section F: 3 candidate questions for the interviewer, mixed genuine + insightful + passion per family F.
5. Identify gaps between the JD and the user's CV/profile (when available). Surface in a "Gaps to address" section.
6. Output: `output/playbook_<company-slug>.md` (create folder if needed). Also present inline.
7. Ask whether to proceed to `mock-interview` using this playbook.

## `mock-interview` mode

1. Follow the session flow in `assets/mock-rubric.md` exactly: greeting → personality + mood capture → warmup → drill rounds (5–8 questions) → trap round → candidate questions round → scorecard.
2. Ask one question at a time via the `question` tool or inline; never reveal the next question before scoring the previous answer.
3. Score each answer on the 5 focus areas + Nugget-First + STAR compliance. Track scores across the session.
4. Inline feedback after each answer: one thing that worked, one thing to improve. 1–2 sentences max.
5. At the end, produce the final scorecard inline (per-focus-area averages, 3 weakest items with concrete re-drill suggestions, trap verdict, overall readiness verdict with 4-tier interviewer-verdict language). Do NOT save to disk unless the user asks.
6. If the user asks to persist, save to `output/mock-scorecard_<date>.md` (create folder if needed).