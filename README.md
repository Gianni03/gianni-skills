# gianni-skills

Personal collection of AI agent skills. Compatible with OpenCode, Claude Code, Gemini CLI, Cursor, Codex, and other agents supported by [Gentle AI](https://github.com/Gentleman-Programming/gentle-ai).

## Skills

| Skill | What it does | Status |
|---|---|---|
| [job-application](skills/job-application/) | Generate personalized job application artifacts: adapted resumes (md+docx+pdf), cover letters, cold outreach, company research, why-this-company, salary reference | Active |

## Install

### Option A: Use the install script

```bash
git clone https://github.com/Gianni03/gianni-skills.git
cd gianni-skills
chmod +x install.sh
./install.sh
```

The script detects which AI agents you have installed and symlinks each skill to the correct path. You can choose which agents to install to.

### Option B: Manual

Copy or symlink the skill folder to your agent's skills directory:

| Agent | Skills path |
|---|---|
| OpenCode | `~/.config/opencode/skills/<skill-name>/` |
| Claude Code | `~/.claude/commands/<skill-name>/` |
| Gemini CLI | `~/.gemini/agents/<skill-name>/` |
| Cursor | `~/.cursor/agents/<skill-name>/` |
| Kiro | `~/.kiro/agents/<skill-name>/` |
| Codex | config TOML, path varies |
| Windsurf | `~/.windsurf/workflows/<skill-name>/` |

Example for OpenCode:

```bash
ln -s "$(pwd)/skills/job-application" ~/.config/opencode/skills/job-application
```

## Cross-Agent Compatibility

All skills use the standard `SKILL.md` format with frontmatter. The skill body is agent-agnostic.

### What works everywhere

All modes that use standard tools (`pdftotext`, `python3`, `libreoffice`, `webfetch`) work in any agent that can read skill files and run shell commands.

### Agent-specific features

| Feature | OpenCode | Claude Code | Gemini CLI | Cursor | Others |
|---|---|---|---|---|---|
| All 6 modes | yes | yes | yes | yes | yes |
| Interactive CV review | yes (uses `question` tool) | manual (chat-based) | manual | manual | manual |
| Profile auto-gen from PDFs | yes | yes | yes | yes | yes |

Interactive mode works best in OpenCode because it uses the `question` tool for structured approval prompts. In other agents, the same flow works conversationally (the AI presents each section and asks for approval in chat).

## Skill Format

Each skill follows the [Gentle AI skill style guide](https://github.com/Gentleman-Programming/gentle-ai/blob/main/docs/skill-style-guide.md):

```
skills/<skill-name>/
  SKILL.md              # Skill contract (frontmatter + rules + execution steps)
  assets/               # Supporting files (templates, scripts, reference docs)
```

## License

Apache-2.0
