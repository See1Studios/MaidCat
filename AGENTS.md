# MaidCat Project Guidelines

Use context7 for up-to-date documentation and examples.

## AI Entry Point Policy

This file serves as the common entry point for all AI coding assistants. We maintain exactly two entry points:
- **AGENTS.md** (this file) - Automatically recognized by GitHub Copilot, Google Antigravity, and OpenAI Codex.
- [CLAUDE.md](CLAUDE.md) - Imports `@AGENTS.md` + Claude-specific instructions (Claude Code does not auto-recognize AGENTS.md).

For Gemini CLI, set `"contextFileName": "AGENTS.md"` in `.gemini/settings.json` or add a single-line `GEMINI.md` (`@AGENTS.md`).

This plugin is installed as a symlink to other Unreal Engine projects via `InstallAsLink.bat`. AI instructions exist **only inside the MaidCat directory**; do not modify the host project root. Users typically open the MaidCat directory as the IDE root.

## Language & Communication Policy

- **User Interaction**: Always communicate and interact with the user in **Korean** (unless explicitly requested otherwise).
- **Communication Style**: Adhere to the communication rules of any dependency marked with `--active` in `requirements.txt` (currently [caveman](file:///C:/Users/parkj/Documents/GitHub/MaidCat/.claude/skills/caveman/SKILL.md): highly compressed, terse, fragments, drop articles/filler/hedging) to save tokens.
- **Documentation & Guidelines**: Write all internal instructions, guidelines (`AGENTS.md`), and domain skill playbooks (`.claude/skills/`) in **English** to optimize context token efficiency and model comprehension.

## Skill & Plugin Dependencies

To maintain consistent behavior across different development environments (such as Google Antigravity, GitHub Copilot, or codon-like AI tools), this project declares external skill/plugin dependencies:
- **Dependency Registry**: Required third-party skills and plugins are declared in [.claude/skills/requirements.txt](file:///C:/Users/parkj/Documents/GitHub/MaidCat/.claude/skills/requirements.txt).
- **Auto-Activation**: Any dependency marked with `--active` flag in `requirements.txt` must be automatically loaded and its rules/styles applied immediately by the AI agent upon project entry.
- **Installation Workflow**: Ensure these skills are populated under `.claude/skills/` before starting:
  - **For Claude Code CLI**: Install using the slash commands (e.g., `/plugin marketplace add <owner/repo>` and `/plugin install <plugin-name>`).
  - **For npm/npx Skill Packages**: Install using `npx skills add <skill-name>`.
  - **For General Agents (Antigravity, Copilot, etc.)**: Download, clone, or unzip the skill folders directly into the `.claude/skills/` directory so they are readable in the workspace.


## Dev Environment

This plugin is developed standalone but runs inside a host Unreal Engine project via symbolic link.
When debugging, testing, or executing commands, check `dev.local.json` (gitignored, project root) for the current host project context:

```json
{
  "host_project_dir": "D:\\UnrealProjects\\See1Unreal",
  "uproject_file":    "D:\\UnrealProjects\\See1Unreal\\See1Unreal.uproject",
  "engine_version":   "5.4"
}
```

- `dev.local.json` is generated automatically by `CreatePluginLink.ps1`.
- If missing, ask the user to run `InstallAsLink.bat` first.
- Logs are located at `{host_project_dir}/Saved/Logs/`.
- Unreal Python stub file is at `{host_project_dir}/Intermediate/PythonStub/unreal.py`. Always verify APIs against this file before writing code.

## General Principles

**Think Before Coding**: Never guess. Always verify against official API docs or the `unreal.py` stub file before writing code. For editor-only properties, check the `__doc__` strings in the stub — they do not appear in `dir()`. For large changes, ask first instead of proceeding unilaterally.

**Simplicity First**: Implement the minimum code that solves the stated problem. Do not add speculative features, unnecessary abstractions, unrequested flexibility, or excessive error handling.

**Surgical Changes**: Touch only the code necessary for the task. Do not improve adjacent code, refactor working functionality, or remove code you did not make unused yourself.

**Goal-Driven Execution**: Translate instructions into verifiable goals with clear success criteria, then execute until those criteria are met.

**No Infinite Loops**: Limit automatic retries for script executions, debugging, or subagent tasks to a maximum of 3 attempts. If a fix fails 3 times, immediately stop and report the error analysis to the user.


## Self-Improvement Loop

We run a self-improvement system that automatically recognizes and records trial-and-error/errors to prevent future mistakes. All AI assistants must perform the following protocol during work:

1. **Recognition**: Identify when an error, unexpected Unreal/TAPython behavior, or environment conflict occurs, and analyze the troubleshooting process.
2. **Decision**: Classify the knowledge domain and select the appropriate recording target:
   - **General Principles / Dev Environment**: Update the relevant section in [AGENTS.md](file:///C:/Users/parkj/Documents/GitHub/MaidCat/AGENTS.md).
   - **Domain Expertise & Playbooks**: Record as a standard Claude Code Skill under `.claude/skills/<skill-name>/`.
     - File path: `.claude/skills/<skill-name>/SKILL.md`
     - Format: Must follow YAML frontmatter (name & description) and body structure.
     - **Benchmarking Best Practices**: Model the skill playbook structure after external best practices (e.g., [karpathy-guidelines](file:///C:/Users/parkj/Documents/GitHub/MaidCat/.claude/skills/karpathy-guidelines/SKILL.md)).
       - **External Reference & Tradeoffs**: Search for existing guidelines (e.g., Github repos, MCP communities). Do not reinvent the wheel. Analyze pros/cons of external solutions before writing.
       - **Actionable Guidelines**: Terse, direct instructions (Do's & Don'ts).
       - **Gotchas & Pitfalls**: Document specific environment/library bugs and how to avoid them based on past trial-and-error.
       - **Comparative Examples**: Show explicit "Correct" vs. "Incorrect" code snippets to anchor comprehension.
3. **Verification (Orchestration)**: For complex or impactful skill/guideline updates, spawn a `self` subagent as an **Auditor**.
   - Direct the Auditor to verify the draft against `unreal.py` API definitions, `karpathy-guidelines`, and syntax/logic correctness.
   - **Autonomous Troubleshooting**: Perform execution tests, script trials, and error handling autonomously with subagents. Avoid prompting the user for trivial step-by-step approvals during debugging. Resolve code errors internally and present only the finalized result.
   - Refine the draft based on the Auditor's peer feedback before proceeding.
4. **Share**: Share the audited knowledge (problem, root cause, prevention, and audit summary) with the user first to propose the skill addition/update.
5. **Record**: Once the user approves or provides feedback, write and build the skill in `.claude/skills/<skill-name>/SKILL.md`.
6. **Journal**: Document the evolution entry (milestones, trials, and learnings) in [.claude/journal.md](file:///C:/Users/parkj/Documents/GitHub/MaidCat/.claude/journal.md) to maintain a transparent development history for the user.





