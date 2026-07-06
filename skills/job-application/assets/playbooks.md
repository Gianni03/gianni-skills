# Job Application Playbooks

Each section is a self-contained playbook for one mode. Load only the section(s) matching the requested mode.

## File Output
- `adapt-resume` generates separate `.md`, `.docx`, and `.pdf` files: `<firstname>_<lastname>_<position-slug>_<company-slug>` in `output/`.
- All other modes (cover-letter, cold-outreach, company-research, why-company, salary-reference) save to a SINGLE `.md` file per company: `<firstname>_<lastname>_application_<company-slug>.md` in `output/`.
- Each mode is a section in the file: `## Cover Letter`, `## Cold Outreach`, `## Company Research`, `## Why This Company`, `## Salary Reference`.
- If the file already exists, update only the relevant section. Do not overwrite other sections.
- Present content inline AND save the file. Report the saved path.

---

# Cover Letter

## Input
- JD text
- Company name + (optional) company About page via webfetch
- Profile raw material (`assets/profile.md`)

## Rules
- Exactly 3 paragraphs.
- Output language = JD language.
- **Paragraph 1. Hook**: open with something SPECIFIC about the company or product (a recent launch, a technical decision, a public value, a product feature). Reference the company by name. Not "I am writing to apply."
- **Paragraph 2. Evidence**: connect exactly 2 concrete achievements from the profile to specific requirements in the JD. Name the metric, the tech, and the impact. Do not list duties. Show causality (achievement then how it maps to what the JD asks).
- **Paragraph 3. CTA**: one-sentence close proposing a conversation. Specific timeframe or a concrete question. No "I look forward to hearing from you."
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
- [ ] No em dashes.

---

# Resume Adaptation

## Input
- JD text
- Job position/title (for file naming)
- Company name (for file naming)
- Profile raw material (`assets/profile.md`)

## Objective
Produce a resume adapted to the JD's keywords and emphasis, WITHOUT fabricating experience. Every claim must trace back to the profile. The adaptation reorders, emphasizes, and rephrases. It does not invent.

## Rules
- **Language**: match the JD language. If JD is English, output English. If Spanish, output Spanish (translate from the source language in profile.md).
- **Keyword alignment**: extract the top 8-12 keywords/technologies from the JD. Ensure each one that appears in the profile (skills or experience) is prominently placed. Do NOT add keywords that aren't backed by real experience.
- **Summary rewrite**: tailor the professional summary to the role. Lead with the most JD-relevant framing of the user's profile.
- **Experience emphasis**: reorder bullet points within each role to put the most JD-relevant achievements first. Rephrase to mirror JD language where truthful.
- **Reverse chronological order**: roles MUST be listed most-recent-first. The current role (Present) always goes first. Never reorder roles by JD relevance. Only reorder bullets within each role.
- **Clickable links**: the contact line MUST use markdown links `[text](url)` for email, portfolio, LinkedIn, and GitHub. Projects (if included) must link to their URLs.
- **Skills section**: reorder to match JD priority order. Add nothing that isn't in profile.md.
- **No fabrication**: if the JD asks for a skill the user doesn't have, do not add it. Instead, emphasize adjacent transferable skills.
- **Project inclusion threshold**: only include projects with a clear, specific connection to a JD requirement. If the connection is weak or generic ("it uses TypeScript"), omit the project. When in doubt, leave it out. A shorter, more relevant Projects section is better than a longer, padded one.
- **Proficiency levels**: `assets/profile.md` classifies skills into three tiers: **Working proficiency** (list in CV Skills section), **Familiar/project-level** (mention only in project context), and **Learning/In Progress** (DO NOT list in CV Skills). Never inflate the CV. When in doubt, omit.
- **Length**: keep to 1 page. Trim least-relevant projects/roles if needed.
- **ATS symbol exclusion (MANDATORY)**: the CV text must NEVER contain `#`, `-`, `/`, `%`, `+`, `*`. The only accepted separator is `|`. These symbols break ATS parsing. Key replacements:
  - "5+ years" -> "5 plus years"
  - "100+" -> "more than 100"
  - "end-to-end" -> "end to end"
  - "30%" -> "30 percent"
  - "UI/UX" -> "UI UX"
  - "Aug 2025 - Present" -> "August 2025 Present" (full month names, space separator)
  - Achievement lines: plain text, NO bullet characters in output

## File generation
1. Write the adapted resume as markdown (with `[text](url)` links) to:
   `output/<firstname>_<lastname>_<position-slug>_<company-slug>.md`
2. Convert to docx (supports clickable hyperlinks):
   `python3 assets/make_docx.py "<input.md>" "<output.docx>"`
3. Convert to PDF (preserves hyperlinks):
   `libreoffice --headless --convert-to pdf "<output.docx>" --outdir output/`
4. Verify 1-page: `pdfinfo "<output.pdf>" | grep Pages`
5. Report all three file paths (.md, .docx, .pdf).

## Markdown structure
```
# <First Name> <Last Name>
<title aligned to JD>
[email](mailto:email) | <location> | [Portfolio](<url>) | [LinkedIn](<url>) | [GitHub](<url>)

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
<language> <level> | <language> <level>

## EDUCATION
<Institution> | <Degree> | <Year>
```

Note: the `#`, `##`, `###`, and `-` are markdown structural markers for the converter only. They do NOT appear in the docx/pdf output. The ATS symbol rules apply to the TEXT CONTENT, not the markdown structure.

## Quality check
- [ ] Every keyword from the JD that exists in the profile appears in the adapted version.
- [ ] No keyword was added that isn't in the profile.
- [ ] Summary leads with the most JD-relevant framing.
- [ ] Roles in reverse chronological order (Present first).
- [ ] Bullets reordered by JD relevance within each role.
- [ ] Contact line has clickable markdown links for email, portfolio, LinkedIn, GitHub.
- [ ] Projects (if included) have clickable links.
- [ ] No forbidden symbols in text content: no #, -, /, %, +, * (only | as separator).
- [ ] Dates use full month names with space separator (August 2025 Present, not Aug 2025 - Present).
- [ ] No bullet characters in docx/pdf output (plain text paragraphs).
- [ ] 1 page max (verify with pdfinfo).
- [ ] .md, .docx, and .pdf all created in output/.

## Interactive Mode

When the user requests interactive mode ("interactive", "paso a paso", "revisar"), generate the CV section by section. For each section:

1. **Present the content** of that section.
2. **Explain WHY** each piece was included:
   - Which JD keyword/requirement it addresses
   - Which data source it came from (profile.md, master PDF)
   - Why this ordering or emphasis was chosen
3. **Ask the user**: keep as is / modify / remove. Use the `question` tool for this. Do not render options as plain text.
4. **Wait for response** before generating the next section. Apply any modifications the user requests.

### Section order:
1. **Professional Summary**. Framing rationale, which JD keywords lead, why this angle.
2. **Work Experience** (role by role). Bullet selection rationale, which JD requirement each bullet maps to, why this order. For each role, explain which bullets were kept/trimmed/added.
3. **Projects**. For each project, explain the specific JD connection. If the connection is weak, flag it and suggest removing. Let the user decide.
4. **Technical Skills**. Which proficiency tier each skill is in (Working / Familiar / Learning), why this ordering, confirm no Learning-tier skills leaked in.
5. **Languages**. Quick confirmation, usually straightforward.
6. **Education**. Quick confirmation, usually straightforward.

### After all sections are reviewed and approved:
- Assemble the final CV markdown from the approved sections.
- Convert to .docx and .pdf.
- Verify 1-page with pdfinfo.
- Report all file paths.

### Key rules:
- **The user is the decision-maker.** If they question a project, bullet, or skill, explain the JD connection honestly. If the connection is weak, agree to remove it. Do not force content the user does not want.
- **Show your reasoning.** The value of interactive mode is transparency. The user sees not just what you included but why.
- **One section at a time.** Do not generate the next section until the current one is approved. This prevents rework.

---

# Cold Outreach

## Input
- Recruiter name, headline, about (from their LinkedIn/profile)
- Company name
- User's role + relevant experience area
- Profile raw material (`assets/profile.md`)

## Rules
- Maximum 4 lines. Not 4 sentences. 4 lines as displayed in a LinkedIn message.
- Output language = the recruiter's profile language (default: English).
- **Line 1. Hook**: reference something SPECIFIC from the recruiter's profile (a post, a hiring focus, a shared connection, their about section). Not "Hi [name], I saw you're hiring."
- **Line 2. Why**: one sentence on why you're reaching out (the role + why you specifically).
- **Line 3. Value**: one line connecting a concrete achievement to what the role needs.
- **Line 4. Ask**: a concrete question or request. NOT "20 minutes of your time." Better: "Would it make sense to connect?" or "Is [role] still open?"
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
- Company URL (optional. Use webfetch on About/Careers/News pages)
- Job position (for tailoring interview questions)

## Rules
Produce a 5-point brief:

1. **Product and Market**: what they sell and to whom (B2B/B2C, target segment, revenue model if public).
2. **Recent News**: 1-2 notable announcements, launches, funding rounds, or leadership changes from the last 6 months. If webfetch yields nothing recent, say so.
3. **Culture Signals**: what their careers page, About page, and public presence communicate about culture (engineering-first? sales-driven? remote-first? values?).
4. **Interview Questions**: 3 specific, intelligent questions the user could ask that show research depth. Tied to the product, the role, or a recent announcement. Not generic.
5. **Red Flags**: any public concerns (layoffs, glassdoor patterns, legal issues, leadership churn). If none found, state "No public red flags identified." Do not invent.

## Sourcing
- Primary: `webfetch` the company's official About/Careers/News pages.
- Secondary: the JD itself (culture signals, tech stack, growth language).
- If webfetch is unavailable: work from JD + user context and explicitly flag which points lack external verification.

## Quality check
- [ ] Each point is specific, not generic.
- [ ] Interview questions reference the company or product, not general software topics.
- [ ] Red flags section is honest. "none found" is a valid answer.

---

# Why This Company

## Input
- Company name
- Company About page (via webfetch, if available)
- JD text
- Profile raw material (`assets/profile.md`)

## Objective
A single short paragraph (3-5 sentences) answering two questions:
1. Why the user wants to work at THIS company (not any company).
2. Why the user is a good match (specific, evidence-based).

## Rules
- Output language = JD language.
- Open with a specific, verifiable detail about the company (a product, a decision, a value, a recent move). NOT a generic "I admire your company."
- Connect that detail to something real in the user's background (a skill, an achievement, a career direction).
- Close with the match: 1-2 concrete reasons from the profile that align with the JD.
- Max 5 sentences. This is a paragraph, not an essay.
- Banned: "innovative", "disruptive", "game-changer", "I have always admired", "it would be an honor", "innovadora".
- **Anti-AI voice rules**: no em dashes (use periods or short sentences instead). No long sentences chained with commas or semicolons. Write like a person talking, not a language model generating prose. Short sentences. Direct. Natural rhythm. Vary sentence length. If a sentence has more than 2 commas, split it.

## Use cases
- Application form "Why do you want to work here?" field
- Email body when applying
- Opening for a longer cover letter

## Quality check
- [ ] Company detail in sentence 1 is specific and verifiable.
- [ ] The "why me" claims trace to the profile, not invented.
- [ ] 5 sentences max.
- [ ] No em dashes.

---

# Salary Reference

## Input
- Job position/title (required)
- Company name + location (required)
- Employment type: contractor or employee (optional. If unknown, explain both)
- Offered USD amount (optional. Only if an offer was received)
- User location (from profile.md, for regional adjustment)

## Objective
Provide a USD reference range so the user knows what to expect or ask for. Works in two modes: **pre-offer** (what should I expect/ask?) and **post-offer** (is this offer fair? should I counter?).

## Rules
Produce a structured response:

### Always (pre-offer and post-offer)
1. **Market range**: typical USD range for this role and seniority. Cite the basis (Levels.fyi, Glassdoor, remote job boards like RemoteOK/Wellfound, industry knowledge). If uncertain, give a range with a confidence note.
2. **Regional adjustment**: how hiring from the user's region affects the range (cost-of-living arbitrage, contractor vs employee). Distinguish "global remote" rates (location-blind) from "geo-adjusted" rates.
3. **What to ask for**: a specific target number or range to aim for, with a one-line rationale.

### If an offer was received (post-offer only)
4. **Offer assessment**: where the offered amount sits relative to the range (below/at/above market). One clear verdict.
5. **Counter-proposal**: a specific counter number to ask for, with a one-line rationale.
6. **Talking points**: 2-3 bullet talking points for the conversation (anchored on value delivered, not cost of living).

## Constraints
- Do NOT fabricate specific salary data. If unsure, say "I cannot verify exact figures. Check [source]" and give a reasoned estimate.
- Distinguish contractor (no benefits, handle own taxes, higher gross) from employee (benefits, lower gross, different tax treatment) if employment type is known. If unknown, explain both scenarios.
- Note regional tax/FX considerations only if relevant to the user's decision.
- This is guidance, not financial advice. State that clearly.

## Quality check
- [ ] Market range has a cited or estimated basis, not a random number.
- [ ] If employment type unknown, both contractor and employee scenarios explained.
- [ ] Target/counter number is specific, not "negotiate higher."
- [ ] Talking points (if post-offer) are value-based, not need-based.
