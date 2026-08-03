# Job Application Playbooks

Each section is a self-contained playbook for one mode. Load only the section(s) matching the requested mode.

## File Output
- `adapt-resume` generates separate `.md`, `.docx`, and `.pdf` files: `Pasquinelli_<position-slug>_<company-slug>`.
- All other modes (cover-letter, cold-outreach, company-research, why-company, salary-reference) save to a SINGLE `.md` file per company: `Pasquinelli_application_<company-slug>.md` in `/home/gianni/Documents/CV/cv_adaptado/`.
- Each mode is a section in the file: `## Cover Letter`, `## Cold Outreach`, `## Company Research`, `## Why This Company`, `## Salary Reference`.
- If the file already exists, update only the relevant section -- do not overwrite other sections.
- Present content inline AND save the file. Report the saved path.

---

# Cover Letter

## Input
- JD text
- Company name + (optional) company About page via webfetch
- Master resume text (pdftotext extract)
- Profile raw material (`assets/profile.md` -- supplementary detail)

## Rules
- Exactly 3 paragraphs.
- Output language = JD language.
- **Paragraph 1 -- Hook**: open with something SPECIFIC about the company or product (a recent launch, a technical decision, a public value, a product feature). Reference the company by name. Not "I am writing to apply."
- **Paragraph 2 -- Evidence**: connect exactly 2 concrete achievements from the resume to specific requirements in the JD. Name the metric, the tech, and the impact. Do not list duties; show causality (achievement -> how it maps to what the JD asks).
- **Paragraph 3 -- CTA**: one-sentence close proposing a conversation. Specific timeframe or a concrete question. No "I look forward to hearing from you."
- Tone: professional but human. Direct, confident, no hedging.
- Banned words: passionate, rockstar, ninja, team player, hard-working, leverage (as a buzzword), "I am excited to", apasionado.
- **Anti-AI voice rules**: no em dashes (use periods or short sentences instead). No long sentences chained with commas or semicolons. Write like a person talking, not a language model generating prose. Short sentences. Direct. Natural rhythm. Vary sentence length. If a sentence has more than 2 commas, split it.
- Do NOT repeat the resume. The cover letter adds narrative, not a summary.

## Quality check before output
- [ ] Company name appears in paragraph 1 with a specific, verifiable detail.
- [ ] Both achievements in paragraph 2 have a number or concrete outcome.
- [ ] Each achievement maps to a JD requirement (not just any achievement).
- [ ] CTA is a single concrete sentence, not a platitude.
- [ ] No banned words.

---

# Resume Adaptation

## Input
- JD text
- Job position/title (for file naming)
- Company name (for file naming)
- Master resume text (pdftotext extract of `gianni_pasqunelli_resume_developer.pdf`)
- Profile raw material (`assets/profile.md` -- supplementary detail: all projects, all skills, achievements trimmed from the PDF)

## Objective
Produce a resume adapted to the JD's keywords and emphasis, WITHOUT fabricating experience. Every claim must trace back to the master resume. The adaptation reorders, emphasizes, and rephrases -- it does not invent.

## Rules
- **Language**: match the JD language. If JD is English, output English resume (master is already English). If Spanish, output Spanish (translate from the English master).
- **Keyword alignment**: extract the top 8-12 keywords/technologies from the JD. Ensure each one that appears in the master resume (skills or experience) is prominently placed. Do NOT add keywords that aren't backed by real experience.
- **Summary rewrite**: tailor the professional summary to the role -- lead with the most JD-relevant framing of Gianni's profile.
- **Experience emphasis**: reorder bullet points within each role to put the most JD-relevant achievements first. Use the user's own language to describe their work. Do NOT parrot JD phrases. The goal is to make relevant experience VISIBLE, not to echo the JD's wording. Keywords belong in the Skills section and naturally in descriptions where truthful, but sentences should sound like the person describing their own work, not like they copied the JD.
- **Anti-parrot rule**: never copy phrases from the JD into the CV. If the JD says "fault-tolerant financial systems", do not write "fault tolerant systems" in the summary. Instead, describe the same concept in the user's own words (e.g., "systems built to handle edge cases without breaking"). The only exception is the Skills section, where technology names (React, TypeScript, REST APIs) are listed as-is because those are factual keywords ATS scanners look for.
- **Reverse chronological order**: roles MUST be listed most-recent-first. The current role (Present / Actualidad) always goes first. Never reorder roles by JD relevance -- only reorder bullets within each role.
- **Clickable links**: the contact line MUST use markdown links `[text](url)` for email, portfolio, LinkedIn, and GitHub. Projects (if included) must link to their URLs. Extract URLs from the master PDF at runtime.
- **Skills section**: reorder to match JD priority order. Add nothing that isn't in the master resume or `assets/profile.md`.
- **No fabrication**: if the JD asks for a skill Gianni doesn't have, do not add it. Instead, emphasize adjacent transferable skills.
- **Project inclusion threshold**: only include projects with a clear, specific connection to a JD requirement. If the connection is weak or generic ("it uses TypeScript"), omit the project. When in doubt, leave it out -- a shorter, more relevant Projects section is better than a longer, padded one.
- **Use profile.md for supplementary detail**: the master PDF is 1 page and curated. `assets/profile.md` has richer material (all projects, all skills, achievements trimmed from the PDF). When the JD asks for something not in the PDF but present in profile.md (e.g., Figma, Jira, financial app project, 3D work), pull it in. Still: do NOT fabricate -- only use what's in profile.md.
- **Proficiency levels**: `assets/profile.md` classifies skills into three tiers: **Working proficiency** (list in CV Skills section), **Familiar/project-level** (mention only in project context), and **Learning/In Progress** (DO NOT list in CV Skills -- courses just finished, not mastered). Never inflate the CV. When in doubt, omit.
- **Length**: 1-2 pages allowed. If content exceeds 1 page, break by complete section — never let a single line or bullet spill onto the next page. Maintain visual balance between pages. A well-structured 2-page resume performs as well or better than a cramped 1-page one.
- **Number formatting**: use numerals with symbols, never spell out quantities or percentages. Write "5+ years", "30%", "100+", "90%", "4 seconds", "20%". Do NOT write "5 plus years", "30 percent", or "more than 100".
- **ATS symbol exclusion (MANDATORY)**: in text content, the CV must NEVER contain `#`, `-`, `/`, `*`. The only accepted separator is `|`. See SKILL.md for the full rules. Key replacements:
  - `%` and `+` ARE ALLOWED with numbers: "5+ years", "30%", "100+", "90%"
  - "end-to-end" -> "end to end"
  - "UI/UX" -> "UI UX"
  - "Aug 2025 - Present" -> "August 2025 Present" (full month names, space separator, NO dash)
  - Achievement lines: plain text, NO bullet characters in output

## File generation
1. Write the adapted resume as markdown (with `[text](url)` links) to:
   `/home/gianni/Documents/CV/cv_adaptado/Pasquinelli_<position-slug>_<company-slug>.md`
2. Convert to docx (supports clickable hyperlinks):
   `python3 "/home/gianni/Documents/CV/skills/job-application/assets/make_docx.py" "<input.md>" "<output.docx>"`
3. Convert to PDF (preserves hyperlinks):
   `libreoffice --headless --convert-to pdf "<output.docx>" --outdir "/home/gianni/Documents/CV/cv_adaptado/"`
4. Verify pages (1-2 allowed): `pdfinfo "<output.pdf>" | grep Pages`
5. Report all three file paths (.md, .docx, .pdf).

## Markdown structure
```
# Gianni Pasquinelli
<title aligned to JD>
[giannipasquinelli@gmail.com](mailto:giannipasquinelli@gmail.com) | Rosario, Argentina | [Portfolio](https://giannipasquinelli-webdev.netlify.app/) | [LinkedIn](https://www.linkedin.com/in/gianni-pasquinelli/) | [GitHub](https://github.com/Gianni03)

## PROFESSIONAL SUMMARY
<adapted summary, no forbidden symbols>

## WORK EXPERIENCE
### <Most Recent Role (Present)> | <Company> | <Month Year Present>
- <reordered bullets, plain text, no forbidden symbols>
### <Previous Role> | <Company> | <Month Year Month Year>
- <reordered bullets>

## PROJECTS
- [Project Name](<url>) | <description, no forbidden symbols>

## TECHNICAL SKILLS
<reordered, pipe separated>

## LANGUAGES
Spanish native | English full professional C1 | Italian limited working

## EDUCATION
UTN | Technical Degree in Programming | Graduated 2025
```

Note: the `#`, `##`, `###`, and `-` are markdown structural markers for the converter only. They do NOT appear in the docx/pdf output. The ATS symbol rules apply to the TEXT CONTENT, not the markdown structure.

## Quality check
- [ ] Every keyword from the JD that exists in the master resume appears in the adapted version.
- [ ] No keyword was added that isn't in the master resume.
- [ ] Summary leads with the most JD-relevant framing.
- [ ] Roles in reverse chronological order (Present first).
- [ ] Bullets reordered by JD relevance within each role.
- [ ] Contact line has clickable markdown links for email, portfolio, LinkedIn, GitHub.
- [ ] Projects (if included) have clickable links.
- [ ] No forbidden symbols in text content: no #, -, /, * in text. % and + ARE allowed with numbers (only | as separator).
- [ ] Numerals with symbols used for quantities: "5+ years", "30%", not "5 plus years" or "30 percent".
- [ ] Dates use full month names with space separator (August 2025 Present, not Aug 2025 - Present).
- [ ] No bullet characters in docx/pdf output (plain text paragraphs).
- [ ] 1-2 pages max. If 2 pages, break by complete section — no lone bullets or lines on page 2 (verify with pdfinfo).
- [ ] .md, .docx, and .pdf all created in cv_adaptado/.

## Interactive Mode

When the user requests interactive mode ("interactive", "paso a paso", "revisar"), generate the CV section by section. For each section:

1. **Present the content** of that section.
2. **Explain WHY** each piece was included:
   - Which JD keyword/requirement it addresses
   - Which data source it came from (master PDF, profile.md, LinkedIn)
   - Why this ordering or emphasis was chosen
3. **Ask the user**: keep as is / modify / remove. Use the `question` tool for this -- do NOT render options as plain text.
4. **Wait for response** before generating the next section. Apply any modifications the user requests.

### Section order:
1. **Professional Summary** -- framing rationale, which JD keywords lead, why this angle
2. **Work Experience** (role by role) -- bullet selection rationale, which JD requirement each bullet maps to, why this order. For each role, explain which bullets were kept/trimmed/added from the source data.
3. **Projects** -- for each project, explain the specific JD connection. If the connection is weak, flag it and suggest removing. Let the user decide.
4. **Technical Skills** -- which proficiency tier each skill is in (Working / Familiar / Learning), why this ordering, confirm no Learning-tier skills leaked in.
5. **Languages** -- quick confirmation, usually straightforward.
6. **Education** -- quick confirmation, usually straightforward.

### After all sections are reviewed and approved:
- Assemble the final CV markdown from the approved sections.
- Convert to .docx and .pdf.
- Verify pages (1-2 allowed) with pdfinfo.
- Report all file paths.

### Key rules:
- **The user is the decision-maker.** If they question a project, bullet, or skill, explain the JD connection honestly. If the connection is weak, agree to remove it. Do not force content the user does not want.
- **Show your reasoning.** The value of interactive mode is transparency -- the user sees not just what you included but why, so they can make informed decisions.
- **One section at a time.** Do not generate the next section until the current one is approved. This prevents rework.

---

# Cold Outreach

## Input
- Recruiter name, headline, about (from their LinkedIn/profile)
- Company name
- Gianni's role + relevant experience area
- Master resume text
- Profile raw material (`assets/profile.md` -- supplementary detail)

## Rules
- Maximum 4 lines. Not 4 sentences -- 4 lines as displayed in a LinkedIn message.
- Output language = the recruiter's profile language (default: English).
- **Line 1 -- Hook**: reference something SPECIFIC from the recruiter's profile (a post, a hiring focus, a shared connection, their about section). Not "Hi [name], I saw you're hiring."
- **Line 2 -- Why**: one sentence on why you're reaching out (the role + why you specifically).
- **Line 3 -- Value**: one line connecting a concrete achievement to what the role needs.
- **Line 4 -- Ask**: a concrete question or request. NOT "20 minutes of your time." Better: "Would it make sense to connect?" or "Is [role] still open?"
- No links. No pitch deck. No attachment mentions. No "I'd love to pick your brain."
- Banned: "Hope this message finds you well", "I came across your profile", "circle back", "touch base", "pick your brain".

## Quality check
- [ ] Line 1 references a specific detail from the recruiter's profile, not a generic greeting.
- [ ] No links or attachments mentioned.
- [ ] The ask is concrete and low-friction, not a meeting request.
- [ ] 4 lines max.

---

# Company Research

## Input
- Company name
- Company URL (optional -- use webfetch on About/Careers/News pages)
- Job position (for tailoring interview questions)

## Rules
Produce a 5-point brief:

1. **Product & Market**: what they sell and to whom (B2B/B2C, target segment, revenue model if public).
2. **Recent News**: 1-2 notable announcements, launches, funding rounds, or leadership changes from the last 6 months. If webfetch yields nothing recent, say so.
3. **Culture Signals**: what their careers page, About page, and public presence communicate about culture (engineering-first? sales-driven? remote-first? values?).
4. **Interview Questions**: 3 specific, intelligent questions Gianni could ask that show research depth -- tied to the product, the role, or a recent announcement. Not generic ("what's the team structure?").
5. **Red Flags**: any public concerns -- layoffs, glassdoor patterns, legal issues, leadership churn. If none found, state "No public red flags identified" -- do not invent.

## Sourcing
- Primary: `webfetch` the company's official About/Careers/News pages.
- Secondary: the JD itself (culture signals, tech stack, growth language).
- If webfetch is unavailable: work from JD + user context and explicitly flag which points lack external verification.

## Quality check
- [ ] Each point is specific, not generic.
- [ ] Interview questions reference the company or product, not general software topics.
- [ ] Red flags section is honest -- "none found" is a valid answer.

---

# Why This Company

## Input
- Company name
- Company About page (via webfetch, if available)
- JD text
- Master resume text
- Profile raw material (`assets/profile.md` -- supplementary detail)

## Objective
A single short paragraph (3-5 sentences) answering two questions:
1. Why Gianni wants to work at THIS company (not any company).
2. Why Gianni is a good match (specific, evidence-based).

## Rules
- Output language = JD language.
- Open with a specific, verifiable detail about the company (a product, a decision, a value, a recent move) -- NOT a generic "I admire your company."
- Connect that detail to something real in Gianni's background (a skill, an achievement, a career direction).
- Close with the match: 1-2 concrete reasons from the resume that align with the JD.
- Max 5 sentences. This is a paragraph, not an essay.
- Banned: "innovative", "disruptive", "game-changer", "I have always admired", "it would be an honor", "innovadora".
- **Anti-AI voice rules**: no em dashes (use periods or short sentences instead). No long sentences chained with commas or semicolons. Write like a person talking, not a language model generating prose. Short sentences. Direct. Natural rhythm. Vary sentence length. If a sentence has more than 2 commas, split it.

## Use cases
- Application form "Why do you want to work here?" field
- Email body when applying
- Opening for a longer cover letter

## Quality check
- [ ] Company detail in sentence 1 is specific and verifiable.
- [ ] The "why me" claims trace to the resume, not invented.
- [ ] 5 sentences max.

---

# Salary Reference

## Input
- Job position/title (required)
- Company name + location (required)
- Employment type: contractor or employee (optional -- if unknown, explain both)
- Offered USD amount (optional -- only if an offer was received)
- Gianni's location: Rosario, Argentina (LATAM)

## Objective
Provide a USD reference range so the user knows what to expect or ask for. Works in two modes: **pre-offer** (what should I expect/ask?) and **post-offer** (is this offer fair? should I counter?).

## Rules
Produce a structured response:

### Always (pre-offer and post-offer)
1. **Market range**: typical USD range for this role and seniority. Cite the basis (Levels.fyi, Glassdoor, remote job boards like RemoteOK/Wellfound, industry knowledge). If uncertain, give a range with a confidence note.
2. **LATAM adjustment**: how hiring from LATAM affects the range (cost-of-living arbitrage, contractor vs employee). Distinguish "global remote" rates (location-blind) from "geo-adjusted" rates.
3. **What to ask for**: a specific target number or range to aim for, with a one-line rationale.

### If an offer was received (post-offer only)
4. **Offer assessment**: where the offered amount sits relative to the range (below/at/above market). One clear verdict.
5. **Counter-proposal**: a specific counter number to ask for, with a one-line rationale.
6. **Talking points**: 2-3 bullet talking points for the conversation (anchored on value delivered, not cost of living).

## Constraints
- Do NOT fabricate specific salary data. If unsure, say "I cannot verify exact figures -- check [source]" and give a reasoned estimate.
- Distinguish contractor (no benefits, handle own taxes, higher gross) from employee (benefits, lower gross, different tax treatment) if employment type is known. If unknown, explain both scenarios.
- Note Argentine tax/fx considerations (dolar MEP/blue, AFIP monotributo vs RL, retentions) only if relevant to the user's decision.
- This is guidance, not financial advice. State that clearly.

## Quality check
- [ ] Market range has a cited or estimated basis, not a random number.
- [ ] If employment type unknown, both contractor and employee scenarios explained.
- [ ] Target/counter number is specific, not "negotiate higher."
- [ ] Talking points (if post-offer) are value-based, not need-based.
