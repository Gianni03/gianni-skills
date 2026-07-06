# Setup Guide — Profile Generation

Run this flow when `assets/profile.md` does not exist. The user provides PDFs and the AI builds their profile.

## Accepted PDF Sources

- **LinkedIn profile export (PDF)**: LinkedIn profile page, "More" button, "Save to PDF". Richest source: all roles, dates, descriptions, skills, education, certifications.
- **Current resume or CV (PDF)**: Any version. The AI cross-references it with LinkedIn.
- **Any other PDF** with professional info (portfolio printout, project documentation, etc.)

## Auto-Generation Flow

1. User puts one or more PDFs in the `assets/` folder.
2. User says "generate my profile" or "generar mi perfil".
3. Run `pdftotext "<pdf-path>" -` for each PDF.
4. Analyze the extracted text. Fill `assets/profile-template.md` with the user's data:
   - Contact info, links, summary, all work experience, all projects, all skills, education, languages.
   - Include any data from the PDFs that is NOT in the 1-page resume (extra projects, skills, achievements).
5. Classify skills into 3 proficiency tiers (see below). Ask the user to confirm which skills are mastered vs. just learning. Do NOT guess.
6. Save as `assets/profile.md`.
7. Present the profile to the user for review. Let them correct anything.

## Manual Option

1. User copies `assets/profile-template.md` to `assets/profile.md`.
2. User fills it manually following the template instructions.
3. User tells the AI when ready.

## Proficiency Tiers (CRITICAL)

When generating profile.md from PDFs, classify every skill into one of three tiers:

- **Working proficiency**: daily use, 2+ years, real production experience. Can list in CV Skills section.
- **Familiar / project-level**: used in specific projects or limited context. Mention only in project descriptions, NOT in Skills section.
- **Learning / In Progress**: courses just finished, not mastered, no production experience. NEVER list in CV Skills section.

Ask the user: "I found these skills in your PDFs. Which ones do you use daily and have 2+ years of production experience? Which ones are from recent courses you haven't applied in production yet?"

The user must confirm. This prevents skill inflation in the generated CV.
