# CLAUDE.md

@AGENTS.md

## Claude Code Specific Instructions

- **Skill System**: Skills inside `.claude/skills/` are automatically triggered via description matching. Follow the defined output format and read the `references/` directory when performing domain tasks.
- **Global User Guidelines**: User global coding guidelines (e.g., DRY, no hardcoding, function segregation) from `~/.claude/CLAUDE.md` are automatically loaded and applied cumulatively. In case of conflict with `AGENTS.md`, the more specific rule takes precedence.
- **Memory System**: The directory `~/.claude/projects/.../memory/` is local to the user's machine. Do not mix it with the plugin wiki/documentation directory. Keep machine-agnostic tips or troubleshooting lessons inside the project `docs/` or `.claude/skills/` registry.
- **File Referencing**: Use the markdown link format `[file.py:42](file.py#L42)` for cross-referencing code locations to support VS Code extension clickable navigation.
