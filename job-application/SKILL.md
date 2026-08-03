---
name: job-application
description: "Trigger: cover letter, cold outreach, adapt resume, adaptar cv, company research, negotiate salary, job application, aplicar a trabajo, carta de presentacion. Generate personalized job application artifacts for Gianni Pasquinelli: cover letters, keyword-adapted resumes (md+docx), recruiter outreach, company briefs, why-this-company paragraphs, and USD salary negotiation."
license: Apache-2.0
metadata:
  author: "giannipasquinelli"
  version: "1.0"
---

## Activation Contract

Use this skill when the user is applying to a job and needs any of: cover letter, resume adapted to JD keywords, cold outreach to a recruiter, company research brief, "why this company" paragraph, or USD salary negotiation guidance. The user provides a job description (JD); the skill produces highly personalized artifacts keyed to Gianni Pasquinelli's profile.

## Hard Rules

- **NEVER modify, edit, or overwrite any file in the CV root folder.** The original CVs are read-only assets.
- **Master resume**: `/home/gianni/Documents/CV/gianni_pasqunelli_resume_developer.pdf` (English). Extract text at runtime with `pdftotext "<path>" -`.
- **Output language matches the JD language.** JD in English -> outputs in English. JD in Spanish -> outputs in Spanish. Detect automatically. The master resume is English; if the JD is Spanish, translate resume content to Spanish when adapting.
- **Adapted CVs go to**: `/home/gianni/Documents/CV/cv_adaptado/` -- create the folder if it does not exist.
- **File naming**: `Pasquinelli_<position-slug>_<company-slug>.md`, `.docx`, and `.pdf` (lowercase, hyphens for spaces). Example: `Pasquinelli_frontend-engineer_acme.md`.
- **Reverse chronological order**: work experience roles MUST be listed most-recent-first. The current role (Present / Actualidad) always goes first. Never reorder roles by JD relevance -- only reorder bullets within each role.
- **Clickable links**: the contact line MUST use markdown links `[text](url)` for email, portfolio, LinkedIn, and GitHub. Projects (if included) must link to their URLs. The `make_docx.py` converter turns these into clickable hyperlinks in .docx and .pdf.
- **ATS symbol exclusion (MANDATORY)**: in text content, the CV must NEVER contain `#`, `-`, `/`, `*`. The only accepted separator is `|`. Rules:
  - `%` and `+` ARE ALLOWED when they accompany numbers (e.g., "5+ years", "30%", "100+", "90%"). They are no longer forbidden — recruiters scan resumes in 6-10 seconds and numerals with symbols stand out visually.
  - `-` in compound words: "end-to-end" -> "end to end", "cross-functional" -> "cross functional"
  - `-` in date ranges: "Aug 2025 - Present" -> "August 2025 Present" (use full month names, space separator, NO dash)
  - `/` in text: "UI/UX" -> "UI UX", "HTML/CSS" -> "HTML and CSS"
  - `#` and `*` must be excluded from text content — they break legacy and small ATS parsers
  - No bullet characters: achievement lines are plain text, not bulleted lists. The markdown uses `-` as a structural marker for the converter, but the docx output renders them as plain indented paragraphs with no bullet symbol.
  - The markdown structural markers (`#`, `##`, `###`, `-`) are fine in the .md source file (the converter strips them). The rule applies to the TEXT CONTENT and the docx/pdf OUTPUT.
- **Number formatting (MANDATORY)**: use numerals with symbols, never spell out quantities or percentages. Write "5+ years", "30%", "100+", "90%", "4 seconds", "20%". Do NOT write "5 plus years", "30 percent", or "more than 100". Numerals with symbols stand out visually during the 6-10 second recruiter scan.
- **Page length**: 1-2 pages allowed. If content exceeds 1 page, break by complete section — never let a single line or bullet spill onto the next page. Maintain visual balance between pages. A well-structured 2-page resume performs as well or better than a cramped 1-page one.
- **Master resume URLs**: extract from the PDF at runtime with: `python3 -c "import re; data=open('<pdf-path>','rb').read(); [print(u.decode()) for u in re.findall(rb'/URI\\s*\\(([^)]+)\\)', data)]"`
- **Profile (raw material)**: `assets/profile.md` contains comprehensive experience, skills, projects, and achievements richer than the 1-page PDF. Read it as supplementary material when adapting CVs -- it has projects (ComunicaYa, RendicionDeCaja, 3D work), skills (Figma, Jira, GitLab, Blender, Notion), and background not in the PDF.
- **Proficiency levels**: `assets/profile.md` classifies skills into three tiers: **Working proficiency** (can list in CV Skills section), **Familiar/project-level** (mention only in context of specific projects), and **Learning/In Progress** (DO NOT list in CV Skills section -- courses just finished, NOT mastered). Never inflate the CV with skills that are not mastered. When in doubt, omit.
- **File output**: `adapt-resume` generates `.md`, `.docx`, and `.pdf` in `cv_adaptado/` with naming `Pasquinelli_<position-slug>_<company-slug>`. All other modes (cover-letter, cold-outreach, company-research, why-company, salary-reference) save to a SINGLE `.md` file per company: `Pasquinelli_application_<company-slug>.md`. Each mode is a section (`## Cover Letter`, `## Cold Outreach`, etc.). If the file already exists, update only the relevant section. Present content inline AND report the saved file path.
- **Personalization is mandatory**: every artifact must reference specifics from the JD, the company, and Gianni's actual achievements. No generic filler, no cliches ("passionate", "team player", "hard worker", "apasionado").
- **No JD parroting**: never copy phrases from the JD into the CV. Use the user's own language to describe their experience. Keywords (technology names) belong in the Skills section. Sentences should sound like the person, not the job description.
- **Company research**: use `webfetch` on the company's About/Careers/News page when a URL or company name is available. If webfetch fails, work from JD + user-provided context and flag the gap.
- **Load the specific playbook** for the requested mode from `assets/playbooks.md` before generating.
- **Interactive mode**: when the user says "interactive", "paso a paso", "revisar", or similar, run `adapt-resume` section by section. Present each section with rationale (why each piece was included, which JD keyword it maps to, data source), then wait for the user to approve/modify/remove before generating the next section. See `## Interactive Mode` in the Resume Adaptation playbook.

## Decision Gates

| User request | Mode | Playbook section |
|---|---|---|
| Cover letter, carta de presentacion | `cover-letter` | `# Cover Letter` |
| Adapt resume, adaptar cv, keywords, interactivo, paso a paso, revisar cv | `adapt-resume` | `# Resume Adaptation` |
| Cold outreach, mensaje reclutador, LinkedIn | `cold-outreach` | `# Cold Outreach` |
| Company research, investigar empresa, brief | `company-research` | `# Company Research` |
| Why this company, por que esta empresa | `why-company` | `# Why This Company` |
| Salary reference, negociar, salary, USD, cuanto pedir, rango salarial | `salary-reference` | `# Salary Reference` |

## Execution Steps

1. Identify which mode(s) the user wants. If ambiguous, ask. Multiple modes can run in one session.
2. Gather inputs:
   - **JD text** (required for all modes) -- paste or file path
   - **Company name** (required for company-research, why-company, cover-letter)
   - **Job position/title** (required for adapt-resume file naming)
   - **Recruiter info** (required for cold-outreach): name, headline, about
   - **Company URL** (optional, for company-research webfetch)
   - **Offered USD amount + employment type** (optional, for salary-reference -- only if an offer was received)
3. Extract master resume text: `pdftotext "/home/gianni/Documents/CV/gianni_pasqunelli_resume_developer.pdf" -`. Also read `assets/profile.md` for supplementary detail (richer than the PDF -- projects, skills, achievements not in the 1-page resume).
4. If company-research or why-company or cover-letter: optionally `webfetch` the company About/Careers page.
5. Read the playbook section for the requested mode(s) from `assets/playbooks.md`.
6. Generate the artifact(s) following the playbook rules exactly.
7. For `adapt-resume` mode: write the adapted CV as `.md` (with markdown links), convert to `.docx` using `python3 assets/make_docx.py <input.md> <output.docx>`, then convert to `.pdf` using `libreoffice --headless --convert-to pdf <output.docx> --outdir <dir>`. Verify pages with `pdfinfo <output.pdf>` (1-2 pages allowed).
8. Present results inline. For files created, report the path(s).

## Output Contract

- `adapt-resume` generates `.md`, `.docx`, `.pdf` in `cv_adaptado/` as `Pasquinelli_<position-slug>_<company-slug>`.
- All other modes (cover-letter, cold-outreach, company-research, why-company, salary-reference) append to a SINGLE file: `Pasquinelli_application_<company-slug>.md` in `cv_adaptado/`. Each mode is a section. If the file exists, update only the relevant section.
- Present content inline AND report the saved file path(s).
- Flag any personalization gaps (e.g., couldn't fetch company page, JD lacked detail).

## References

- Master resume: `/home/gianni/Documents/CV/gianni_pasqunelli_resume_developer.pdf`
- Profile (raw material): `assets/profile.md`
- Playbooks: `assets/playbooks.md`
- docx converter: `assets/make_docx.py`
