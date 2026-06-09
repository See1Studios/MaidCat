# Claude Code Skill Registry

This directory manages project-specific custom skills (playbooks) following the **Claude Code Skill System specification**.

## 🛠️ Skill Directory Structure
Each skill has its own subdirectory configured as follows:
- `.claude/skills/<skill-name>/SKILL.md`: Skill metadata (YAML Frontmatter) and playbook body (Required).
- `.claude/skills/<skill-name>/scripts/`: Executable scripts used by the skill (Optional).
- `.claude/skills/<skill-name>/references/`: Reference docs or API stubs (Optional).

## 📝 SKILL.md Template
```yaml
---
name: <skill-name-kebab-case>
description: <3rd-person description for progressive disclosure matching (200-1000 chars)>
---

# <Skill Name> Playbook

## Instructions
- Directive 1
- Directive 2

## Examples
- Sample code or configuration blocks
```

## 🌐 Useful Community Repositories
Here are some high-quality public repositories and registries containing Claude Code plugins, skills, and playbooks that can be used to boost productivity:

- **[anthropics/skills](https://github.com/anthropics/skills)**: The official Anthropic reference repository for agent skills and specifications.
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)**: A curated list of excellent skills, hooks, and plugins.
- **[travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)**: A comprehensive directory focused specifically on custom skills.
- **[ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins)**: A registry of plugins extending Claude Code with various MCP servers and tools.
- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)**: A large collection of community-contributed skills and plugins.
