#!/usr/bin/env bash
# install.sh — Install skills from gianni-skills to detected AI agents.
# Usage: ./install.sh [--agent <name>] [--force]
# Without flags, detects all installed agents and installs to all.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"
FORCE=false

# Parse args
AGENT_FILTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_FILTER="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    --help|-h)
      echo "Usage: ./install.sh [--agent <name>] [--force]"
      echo ""
      echo "Agents: opencode, claude, gemini, cursor, kiro, windsurf"
      echo "Without --agent, installs to all detected agents."
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Agent definitions: name | skills path | detect command
declare -a AGENTS=(
  "opencode|${HOME}/.config/opencode/skills|command -v opencode"
  "claude|${HOME}/.claude/commands|test -d ${HOME}/.claude"
  "gemini|${HOME}/.gemini/agents|command -v gemini"
  "cursor|${HOME}/.cursor/agents|test -d ${HOME}/.cursor"
  "kiro|${HOME}/.kiro/agents|test -d ${HOME}/.kiro"
  "windsurf|${HOME}/.windsurf/workflows|test -d ${HOME}/.windsurf"
)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

install_skill() {
  local skill_dir="$1"
  local target_dir="$2"
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local target_path="${target_dir}/${skill_name}"

  # Create target dir if needed
  mkdir -p "$target_dir"

  # Remove existing if force
  if [[ -L "$target_path" || -d "$target_path" ]]; then
    if $FORCE; then
      rm -rf "$target_path"
    else
      echo -e "  ${YELLOW}SKIP${NC} ${skill_name} (already exists, use --force to overwrite)"
      return 0
    fi
  fi

  # Symlink
  ln -s "$skill_dir" "$target_path"
  echo -e "  ${GREEN}OK${NC}   ${skill_name} -> ${target_path}"
}

# Find all skills
SKILLS=()
if [[ -d "$SKILLS_DIR" ]]; then
  for dir in "$SKILLS_DIR"/*/; do
    [[ -f "${dir}SKILL.md" ]] && SKILLS+=("$(cd "$dir" && pwd)")
  done
fi

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "No skills found in ${SKILLS_DIR}"
  exit 1
fi

echo "Found ${#SKILLS[@]} skill(s): ${SKILLS[*]##*/}"
echo ""

# Install to each detected agent
INSTALLED_ANY=false
for agent_def in "${AGENTS[@]}"; do
  IFS='|' read -r name path detect <<< "$agent_def"

  # Filter by --agent if specified
  if [[ -n "$AGENT_FILTER" && "$name" != "$AGENT_FILTER" ]]; then
    continue
  fi

  # Detect
  if eval "$detect" >/dev/null 2>&1; then
    echo "Installing to ${name} (${path})..."
    for skill in "${SKILLS[@]}"; do
      install_skill "$skill" "$path"
    done
    INSTALLED_ANY=true
    echo ""
  else
    echo -e "${YELLOW}SKIP${NC} ${name} (not detected)"
  fi
done

if ! $INSTALLED_ANY; then
  echo -e "${RED}No AI agents detected.${NC}"
  echo "Install an agent first (opencode, claude, gemini, cursor, etc.) or specify manually:"
  echo "  ./install.sh --agent opencode"
  exit 1
fi

echo "Done. Restart your AI agent to load the new skills."
