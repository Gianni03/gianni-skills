# ATS Symbol Exclusion Rules

In text content, the CV must NEVER contain these symbols: `#`, `-`, `/`, `*`. The only accepted separator is `|`.

**Allowed with numbers**: `%` and `+` are no longer forbidden when they accompany numbers — use "5+ years", "30%", "100+", "90%". Recruiters scan resumes in 6-10 seconds and numerals with symbols stand out visually. Do NOT spell out quantities or percentages ("5 plus years" and "30 percent" are wrong — write "5+ years" and "30%").

## Replacement Table

| Forbidden | Replacement | Example |
|---|---|---|
| `-` in compound words | space | "end-to-end" -> "end to end", "cross-functional" -> "cross functional" |
| `-` in date ranges | full month names, space separator, NO dash | "Aug 2025 - Present" -> "August 2025 Present" |
| `/` in text | space or "and" | "UI/UX" -> "UI UX", "HTML/CSS" -> "HTML and CSS" |
| `#` in text | remove or rephrase | `#` breaks legacy and small ATS parsers |
| `*` in text | remove or rephrase | `*` breaks legacy and small ATS parsers |
| Bullet characters | none (plain paragraphs) | Achievement lines are plain indented text, no bullet symbol in docx/pdf output |

## Markdown Source vs Output

The markdown structural markers (`#`, `##`, `###`, `-`) are fine in the `.md` source file. The `make_docx.py` converter strips them. The ATS rules apply to the TEXT CONTENT and the docx/pdf OUTPUT only.

## Verification

After generating the PDF, verify no forbidden symbols leaked (note: `%` and `+` are allowed, so they are NOT in the regex):

```bash
pdftotext "<output.pdf>" - | grep -nE '[-#*/]'
```

Empty output means clean.
