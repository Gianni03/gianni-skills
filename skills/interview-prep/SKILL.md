---
name: interview-prep
description: "Trigger: interview prep, mock interview, preparar entrevista, personalidad entrevista, simulacro, cultural fit, behavioral, preguntas entrevista. Generate interview preparation: personality strategy (mood-aware), interview playbook (per-JD), interactive mock interview with scoring. All three modes run interactively."
license: Apache-2.0
metadata:
  author: "giannipasquinelli"
  version: "1.0"
---

## Activation Contract

Use when the user is preparing for an interview and wants any of: an interview strategy based on their personality type and today's mood, a preparation playbook keyed to a specific job description (behavioral/cultural-fit/soft-skill focus), or an interactive mock interview with live scoring and feedback. The user may ask for one mode or run all three in sequence.

Always load the methodology assets before generating. The corpus is local PDFs in `assets/pdfs/`; read `assets/methodology.md` as the canonical synthesis and descend into PDFs only when deeper context is required.

The user's declared mood matters — never skip the mood capture in `personality-strategy` mode.

## Hard Rules

- **Behavioral, cultural-fit, and soft-skill focus only.** Do NOT do leetcode, algorithm, or system-design prep. If the user asks for algorithm prep, explain that is out of scope and suggest a separate skill.
- **Only Interviewology's Four Interview Styles** (Charmer / Challenger / Examiner / Harmonizer) is the personality system. Do NOT use DISC, MBTI, Big Five, or Enneagram. If the user asks for a different system, explain the corpus uses Interviewology and offer to add their source.
- **Output language matches the JD language** (English JD → English output; Spanish JD → Spanish output; no JD → match the user's last message language; English fallback).
- **All three modes are interactive**: ask clarifying questions; never silently produce a wall of text. Use the `question` tool when presenting explicit choices.
- **No fabrication.** If the corpus doesn't cover a question, say so and offer an evidence-based analog from the same family.
- **No salary negotiation content.** That lives in the `job-application` skill's `salary-reference` mode. Cross-reference, do not duplicate.
- **No body language / video etiquette / stress management coaching** unless the user explicitly asks. The corpus has only passing mentions; do not fabricate depth.
- **Nugget First + STAR is the default answer structure** for every behavioral example produced or scored. Lead with a one-line nugget, then Situation, Task, Action (use "I", not "we"), Result.
- **Reuse `job-application` artifacts when available.** If the user ran `company-research` or `adapt-resume` in this session, pull that output to inform the playbook's cultural-fit questions and the elevator pitch. Do not re-fetch.
- **Read `assets/methodology.md` first** for any mode. Read `assets/personality-cheatsheet.md` for `personality-strategy`. Read `assets/question-bank.md` for `playbook` and `mock-interview`. Read `assets/mock-rubric.md` for `mock-interview` scoring mechanics.

## Decision Gates

| Need | Action |
|---|---|
| Quick strategy for an upcoming interview today | `personality-strategy` mode — mood-aware coaching |
| Full per-JD prep doc (questions, answers strategy, gaps, candidate questions) | `playbook` mode |
| Live rehearsal with scoring | `mock-interview` mode |
| Full sequence (strategy → playbook → mock) | Run modes in that order; pass outputs as inputs |
| User has run `job-application` in this session | Reuse `company-research` and `adapt-resume` outputs as playbook inputs |
| Image-only assets needed | Defer: OCR was not run; ask the user to install `tesseract` and re-export, or skip |
| Notion exports needed | Check `assets/external-links.md`; if the user has exported pages drop them under `assets/notion-exports/` |
| Long methodology context | Stay in `assets/methodology.md`; do not paste full PDFs inline |
| Behavioral question templates | Use `assets/question-bank.md`; descend into PDFs only for trap-question coaching |

## Execution Steps

1. Read `assets/methodology.md` to ground yourself in the synthesized frameworks.
2. Identify which mode the user wants. If ambiguous, ask via the `question` tool. Multiple modes can run in one session.
3. For each requested mode:

   **`personality-strategy` mode**:
   1. Walk the "Which line lands?" diagnostic from `assets/personality-cheatsheet.md`. If the user already declared a primary style (this session or carried from `job-application`), confirm it instead of re-asking.
   2. Ask for today's mood via the `question` tool: motivated / eager / cautious / discouraged / defensive / neutral.
   3. Map the mood to the overlay per the personality-cheatsheet mood table.
   4. Generate the strategy document: primary style profile, today's overlay, best opening advice, two traps to watch for, two answer-structure reminders (Nugget First + STAR). Present inline.
   5. Ask whether to proceed to `playbook` or `mock-interview`.

   **`playbook` mode**:
   1. Request the JD (paste or file path). If no JD, ask whether to run a general rehearsal or stop and require one. Cultural-fit questions benefit significantly from a JD — do not fabricate them without one.
   2. If a JD is provided, optionally `webfetch` the company site (or reuse `job-application`'s `company-research` output).
   3. Use `assets/question-bank.md` families A through E. Select from each:
      - A (self-introduction + narrative): one elevator pitch ✍️ exercise + one "why this company" answer skeleton.
      - B (strengths & weaknesses): one strengths, one weakness with the trap-handling coaching.
      - C (behavioral/STAR): 3–5 questions selected by JD signal keywords. Provide an answer strategy for each, NOT a fully scripted answer (the user should voice their own version).
      - D (leadership & teamwork): one question selected by JD seniority signals.
      - E (cultural-fit + trap): two E questions where one is a trap question. Include the "what NOT to do" coaching for the trap.
   4. Generate section F: 3 candidate questions for the interviewer, mixed genuine + insightful + passion per `assets/question-bank.md` family F.
   5. Identify the gaps between the JD and the user's CV/profile (when available) and surface them in a "Gaps to address" section.
   6. Output: `output/playbook_<company-slug>.md` (create the folder if needed). Also present inline.
   7. Ask whether to proceed to `mock-interview` using this playbook.

   **`mock-interview` mode**:
   1. Follow the session flow in `assets/mock-rubric.md` exactly: greeting → personality + mood capture → warmup → drill rounds (5–8 questions) → trap round → candidate questions round → scorecard.
   2. Ask one question at a time via the `question` tool or inline; never reveal the next question before scoring the previous answer.
   3. Score each answer on the 5 focus areas + Nugget-First + STAR compliance. Track scores across the session.
   4. Inline feedback after each answer: one thing that worked, one thing to improve. Keep it to 1–2 sentences.
   5. At the end, produce the final scorecard inline (per-focus-area averages, 3 weakest items with concrete re-drill suggestions, trap verdict, overall readiness verdict). Do NOT save to disk unless the user asks.
   6. If the user asks to persist, save to `output/mock-scorecard_<date>.md` (create the folder if needed).

4. Present outputs inline. For files created, report the path(s).
5. Ask whether to run the next mode or stop.

## Output Contract

- **Content**: every artifact must be personality-aware (uses the archetype + overlay from `personality-strategy`), evidence-backed (traceable to the JD or the user's profile), and structured. No generic filler. No cliches ("passionate", "team player", "apasionado").
- **Files**:
  - `personality-strategy` produces inline output only. No file.
  - `playbook` saves to `output/playbook_<company-slug>.md`.
  - `mock-interview` saves inline by default; `output/mock-scorecard_<date>.md` only if the user asks.
- **Language**: match JD language (or user message language if no JD), with neutral/professional register.
- **Gaps**: always flag any gap you could not cover (e.g. "the JD asked for X leadership frame; the corpus doesn't cover that angle — using the closest C-family question instead").

## Folder structure

```
skills/interview-prep/
├── SKILL.md                          # This file — runtime contract
├── assets/
│   ├── methodology.md               # Canonical synthesis — READ FIRST for every mode
│   ├── personality-cheatsheet.md    # Four Styles profiles + mood overlay — for personality-strategy
│   ├── question-bank.md             # Consolidated taxonomy — for playbook and mock-interview
│   ├── mock-rubric.md               # Scorcard + drill mechanics — for mock-interview
│   ├── external-links.md            # Notion links + image OCR status — pending ingestion
│   └── pdfs/                        # Source corpus (5 PDFs; coding-interview.pdf excluded)
│       ├── Interviewology_Anna_Papalia.pdf
│       ├── metainterview.pdf
│       ├── preguntas-entrevista-y-tips.pdf
│       ├── preguntas y respuestas entrevista.pdf
│       └── Frontend_Interview_Preparation_Handbook.pdf
└── output/                           # Generated artifacts at runtime — create if needed
    ├── playbook_<company-slug>.md
    └── mock-scorecard_<date>.md
```

## References

- `assets/methodology.md` — canonical synthesis of the 6-PDF corpus (read first).
- `assets/personality-cheatsheet.md` — Four Styles profiles + self-identification heuristic + mood overlay mechanics.
- `assets/question-bank.md` — behavioral/cultural-fit/soft-skill question taxonomy by family.
- `assets/mock-rubric.md` — session flow + 5 focus areas scoring grid + trap question criteria + feedback mechanics.
- `assets/external-links.md` — Notion links (private, pending export) and public references.
- `assets/pdfs/` — the source corpus.