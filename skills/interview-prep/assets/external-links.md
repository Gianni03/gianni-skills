# External References — Not鞠 yet ingested

Additional reference material the user has identified for the `interview-prep` skill. These links are NOT ingested into the local corpus; fetch or export them as the skill evolves. New items go at the bottom.

## Notion (private — requires login)

- **Avature interviews** — https://app.notion.com/p/gianni-03/Avature-interviews-11ff2b34444680659faac35202a1ccc6
  - Status: INGESTED. See `notion-exports/avature.md`.

- **Interview Ready** — https://app.notion.com/p/gianni-03/Interview-Ready-2c9f2b3444468092adc5c3845169f111
  - Status: INGESTED. See `notion-exports/interview-ready.md`.

- **Test de personalidad** — https://app.notion.com/p/gianni-03/Test-personalidad-04708f55d9f14c08807d636d666c11a9
  - Status: NOT INGESTED. The Notion page is just links to external personality-test sites (no original content). The two external sites it points to were checked 2026-07-23 and yielded NOTHING usable:
    - 16personalities.com — login-walled; uses the NERIS framework (loosely Big Five-based), which is OUT OF SCOPE per the SKILL.md hard rule "Only Interviewology's Four Interview Styles". Do NOT ingest.
    - secure.plum.io — login-walled SPA, no extractable content.
  - Decision: skip permanently. The `personality-strategy` mode stays on Interviewology only.

## Public web pages (fetched, low-to-medium relevance for interview-prep)

- **GetManfred — Helping Juniors** — https://www.getmanfred.com/helping-juniors
  - Fetched 2026-07-23. Spanish wiki about starting a tech career. Generic CV/interview tips. No new framework. Relevance: low for interview-prep specifically (overlaps with `job-application`). Reused if the user ever asks for "junior angle" content in mock-interview drills.

- **Getting The Front End Job** — https://getting-the-front-end-job.surge.sh/
  - Fetched 2026-07-23. A free online book. TOC: Introduction → The Three Users (HR Recruiters, Tech Lead) → Technologies → Building the Resume → Lunch (humor section) → GitHub employer-ready → Portfolio → Macro To Micro Content. Most relevant section for interview-prep: `/introductory-pitch` and `/the-tech-lead` (likely covers tech-lead interview dynamics).
  - Relevance: medium. The "Introductory Pitch" section is closely related to family A of the question bank.
  - How to ingest deeper: `webfetch` the specific chapter pages when the `personality-strategy` or `playbook` mode needs that nuance; no need to bulk-import now.

## Image-only assets (OCR pending)

The source folder also contained image files that have NOT been processed (OCR was unavailable at build time). They live in `/home/gianni/Desktop/Programacion - libros/Entrevistas/` and `/home/gianni/Desktop/Programacion - libros/Entrevistas/entrevista-ingles/`:

- `ENTREVISTA.png` — 497KB
- `entrevistas.jfif` — 141KB
- `preguntarEnEntrevistas.png` — 210KB
- `preguntasEntrevista.jfif` — 174KB
- `entrevista-ingles/` — 5 JPG files (0–4)

How to ingest later: install `tesseract` and `pdftotext`-style flow does not apply; use `tesseract <image> out` per image, clean up, and drop the resulting `.txt` files into `assets/ocr-exports/`. The skill will read them automatically.