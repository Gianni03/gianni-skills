# Interview Methodology — Synthesized Frameworks

This file synthesizes the interview-prep methodology from the corpus in `assets/pdfs/`. It is the primary knowledge source for the `interview-prep` skill. Refer back to the PDFs only when deeper context is needed.

## 1. The Four Interview Styles (Anna Papalia, *Interviewology*)

The corpus's sole personality-typing system. Scientifically validated (ASI Construct Validity). Built conceptually on Howard Gardner's *Frames of Mind* but is its own system. Not DISC, not MBTI, not Big Five.

### Two orthogonal axes

- **Axis 1 — Energy**: Introversion (energized by alone time, think-to-speak) ↔ Extroversion (energized by people, speak-to-think)
- **Axis 2 — Orientation**: Steadfast (internally focused, consistent, unwavering) ↔ Accommodating (externally focused, adaptive, reads the room)

### The four archetypes (quadrant map)

| | Extroverted | Introverted |
|---|---|---|
| **Accommodating** | **Charmer** — wants to be liked; performance; eager; fear: not being accepted | **Harmonizer** — wants to adapt/fit in; team tryout; agreeable; fear: not belonging |
| **Steadfast** | **Challenger** — wants to be heard; cross-examination; questioning; fear: not respected | **Examiner** — wants to get it right; graded test; precise; fear: vulnerability |

### 12 sub-variants

Each primary style has 2 neighbor-tendency variants (hexagonal adjacency): Charmer/Harmonizer, Charmer, Charmer/Challenger; Challenger/Charmer, Challenger, Challenger/Examiner; Examiner/Challenger, Examiner, Examiner/Harmonizer; Harmonizer/Examiner, Harmonizer, Harmonizer/Charmer.

### Per-archetype primitives (use directly in `personality-strategy` mode)

For each archetype the corpus defines: priority line (what they want), show-value line (how they demonstrate worth), interview-as metaphor (how they frame the event), at-worst verb (failure mode), advice-to-self, focus (internal vs external), time orientation (past→future vs present), drawn-to (complementary style), opposite style.

Load `assets/personality-cheatsheet.md` for the structured per-archetype table.

### "Mood of the day" overlay (skill-invented layer)

The corpus treats style as a snapshot that CAN shift (88% year-over-year stable, but e.g. an Examiner who built confidence became a Charmer). The skill invents a mood overlay on this premise:

- The primary style is the user's baseline (self-identified via `personality-cheatsheet.md` heuristic).
- The mood is a **temporary lean toward a neighboring style's tendencies**. Examples:
  - Examiner excited about the company → temporary Charmer eagerness in opening
  - Harmonizer under stress → temporary Challenger-steadfast in questioning
  - Charmer coming off a confidence dip → Examiner-steadfast deliberateness
- The user declares the mood (motivated / cautious / discouraged / eager / defensive). The skill maps the declared mood to a neighboring-tendency adjustment and surfaces which advice and which answer-pacing to emphasize THIS session.
- The skill never overrides the primary style — it overlays.

## 2. STAR / S.A.R. + Nugget First (cross-corpus)

### Standard STAR (Situation, Task, Action, Result)

The dominant answer-structuring method. Appears in Interviewology, metainterview, Frontend Handbook (literal S-T-A-R). Definitions:

- **Situation**: the context, in one or two sentences
- **Task**: your specific responsibility in that situation
- **Action**: what YOU did (use "I", not "we"), concrete and specific
- **Result**: the measurable outcome, with numbers when possible

### Cracking's S.A.R. + Nugget First refinement

*S.A.R.* is STAR with Task folded into Situation. The Nugget-First technique (from *Cracking the Coding Interview*) layers on top of ANY variant:

1. **Nugget**: one-line summary that captures the gist of the story (delivered first, before Situation)
2. Then walk through S → A → R

This works because interviewers form their impression in the first 10 seconds; leading with the nugget gets the headline across, then the structure proves it.

### Cracking's behavioral prep grid (use as self-audit checklist)

Six rows; for each, the user brainstorms 1–3 stories from their own resume:
1. Challenges
2. Mistakes / Failures
3. Enjoyed
4. Leadership
5. Conflicts
6. What You'd Do Differently

Build this grid BEFORE the interview. Each cell seeds a STAR story.

### "Use I, not we" rule

When describing actions in STAR stories, the interviewer hears "we" as "I didn't do anything." Use "I" even when the work was collective. Be specific about YOUR contribution.

## 3. The 5 Behavioral Focus Areas (Meta / metainterview.pdf)

The strongest explicit scoring rubric in the corpus. Use as the rubric for `mock-interview` mode, and as a cross-check when generating the `playbook`.

1. **Resolving conflict**: What kind of disagreements have you had with colleagues/managers? How have you resolved them?
2. **Growing continuously**: How have you approached improving your skills?
3. **Embracing ambiguity**: How do you operate in an ambiguous and quickly changing environment?
4. **Driving results**: How do you demonstrate your impact? Are you self-directed in reaching goals?
5. **Communicating effectively**: How well do you communicate with teams and cross-functional partners?

For the `mock-interview` mode, each user answer is scored 0–3 against each of the 5 focus areas. Load `assets/mock-rubric.md` for the scoring grid and drill mechanics.

## 4. Question archetypes (taxonomy overview)

Six behavioral/cultural-fit/soft-skill question families are catalogued in `assets/question-bank.md`:

- A. Self-introduction & narrative
- B. Strengths & weaknesses (trap questions)
- C. Behavioral / experience (STAR-eliciting)
- D. Leadership & teamwork
- E. Cultural fit & company research
- F. Questions to ask the interviewer

Each family has English and Spanish entries. The `playbook` mode selects from these families based on the JD; the `mock-interview` mode drills from them sequentially.

Complementary cut. The Avature corpus provides a trait-keyed bank grouping questions by assessed competency (Adaptability, Ownership, Listening, etc.) with explicit assessment cues. Use this second axis when a JD names a specific competency — pull from family G in `question-bank.md` rather than re-phrasing from A-F.

## 5. Trap / difficult questions (Spanish corpus)

The *preguntas y respuestas entrevista.pdf* document defines two question archetypes that need specialized handling:

- **Preguntas trampa** (trap questions): "What do you like (and dislike) about your current job?", "How long would you stay with us?", "Are you in other selection processes?" — designed to expose negativity, dishonesty, or desperation.
- **Preguntas difíciles** (difficult questions): "Cuéntame un poco sobre ti...", "Why should we hire you?", "Why are you changing jobs?", "What is your greatest weakness?" — designed to trigger rambling or generic answers.

Each trap/difficult question has a paired "what NOT to do / what to do" coaching in the source PDF. The `playbook` mode should produce trap-question handling guidance per-JD; the `mock-interview` mode should include at least one trap-question drill per session.

## 6. Scope limits (what this skill does NOT do)

- **No leetcode / algorithm prep.** The coding-interview.pdf corpus (Cracking the Coding Interview) is explicitly out of scope. If the user wants algorithm prep, that is a different skill.
- **No DISC / MBTI / Big Five / Enneagram.** Only Interviewology's 4 styles are supported; if the user asks for another typing system, explain that the corpus uses Interviewology and offer to add the system's source if provided.
- **No salary negotiation.** That lives in the `job-application` skill's `salary-reference` mode. Don't duplicate.
- **No body language / video etiquette / stress management.** The corpus has only passing mentions; this skill will not fabricate guidance in those areas.

## 7. Strong Yes lever

A Strong Yes is a single interviewer who becomes a champion — they actively advocate for the candidate in the hiring committee. S-Tier companies often require at least one Strong Yes regardless of Soft-Yes votes. The leverage to convert a Yes into a Strong Yes is human connection (rapport, curiosity, fit perceived by the interviewer), not pure technical ability. Source: interview-ready.md. This reframes the goal of `personality-strategy` mode: connect as the archetype's 'best opening' suggests, not just land the answer cleanly.

## 8. Sources

- `assets/pdfs/Interviewology_Anna_Papalia.pdf` — primary personality source
- `assets/pdfs/metainterview.pdf` — behavioral rubric + STAR confirmation
- `assets/pdfs/preguntas y respuestas entrevista.pdf` — Spanish trap/difficult question bank
- `assets/pdfs/preguntas-entrevista-y-tips.pdf` — Spanish soft-skill + cultural-fit input
- `assets/pdfs/Frontend_Interview_Preparation_Handbook.pdf` — elevator pitch + STAR anchor
- *Cracking the Coding Interview* (McDowell) — S.A.R. + Nugget First + behavioral prep grid + "I not we" rule. Not shipped in repo (56MB, LOW relevance); technique attribution only.
- `assets/notion-exports/avature.md` — internal company rubric (cultural skills + behavioral question pool only; technical rubric excluded as out-of-scope).
- `assets/notion-exports/interview-ready.md` — personal playbook (Strong Yes lever, turn-around tactics, graded-answer gallery, storytelling DO/DON'Ts, canonical cultural sequence; salary/technical sections excluded as job-application or out-of-scope territory).