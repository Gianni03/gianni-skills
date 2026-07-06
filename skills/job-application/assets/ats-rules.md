# ATS Symbol Exclusion Rules

The CV text must NEVER contain these symbols: `#`, `-`, `/`, `%`, `+`, `*`. The only accepted separator is `|`. These symbols break ATS (Applicant Tracking System) parsing.

## Replacement Table

| Forbidden | Replacement | Example |
|---|---|---|
| `+` after numbers | "plus" | "5+ years" -> "5 plus years", "100+" -> "more than 100", "+15" -> "15 plus" |
| `-` in compound words | space | "end-to-end" -> "end to end", "cross-functional" -> "cross functional" |
| `-` in date ranges | full month names, space separator | "Aug 2025 - Present" -> "August 2025 Present" |
| `/` in text | space or "and" | "UI/UX" -> "UI UX", "HTML/CSS" -> "HTML and CSS" |
| `%` after numbers | "percent" | "30%" -> "30 percent", "90%" -> "90 percent" |
| Bullet characters | none (plain paragraphs) | Achievement lines are plain indented text, no bullet symbol in docx/pdf output |

## Markdown Source vs Output

The markdown structural markers (`#`, `##`, `###`, `-`) are fine in the `.md` source file. The `make_docx.py` converter strips them. The ATS rules apply to the TEXT CONTENT and the docx/pdf OUTPUT only.

## Verification

After generating the PDF, verify no forbidden symbols leaked:

```bash
pdftotext "<output.pdf>" - | grep -nE '[-#%+*/]'
```

Empty output means clean.
