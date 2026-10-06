# Prompt library

Sixteen VS Code Copilot agent-mode prompt files (`*.prompt.md`), each with `description` and `agent: 'agent'` frontmatter and the same skeleton: Mission, Scope and Preconditions, Workflow, Output Expectations, Quality Assurance. They activate when this folder's parent is the VS Code workspace root. For Claude Code the equivalents are skills or a `CLAUDE.md`; none exist yet.

| File | Use it when |
|---|---|
| `product-discovery.prompt.md` | Before writing code: six forcing questions, three approaches, a DESIGN.md |
| `implementation-plan.prompt.md` | Turning a design into 2 to 5 minute tasks with verification steps (PLAN.md) |
| `project-development.prompt.md` | Building a project end to end from existing docs (keeps TODO.md) |
| `backend.prompt.md` | Backend architecture, DevOps pipelines, cost guardrails and model routing |
| `ui-ux-design.prompt.md` | Any UI work: accessibility first, then touch, performance, style, layout, type, motion, forms, navigation, charts |
| `code-organization.prompt.md` | Restructuring a codebase without changing behaviour |
| `tdd.prompt.md` | Strict red-green-refactor |
| `testing.prompt.md` | Manual test guide plus automated verification before deployment |
| `code-review.prompt.md` | Single-pass review with BLOCKER / SUGGESTION / NIT markers |
| `security-audit.prompt.md` | OWASP Top 10 plus STRIDE, high-confidence findings only |
| `system-audit.prompt.md` | Seven-phase audit with a 0 to 10 scoring dashboard and fix plan |
| `investigate.prompt.md` | Root-cause debugging; stop after three failed fixes |
| `ship.prompt.md` | Sync, test, coverage, push, PR, CI |
| `weekly-retro.prompt.md` | Data-driven weekly retrospective from git history |
| `chat-history.prompt.md` | Append a session log to `chat-history/` in the repo |
| `safety-guardrails.prompt.md` | Warn before destructive commands (advisory only; not enforced by Copilot) |

## Notes

- `security-audit.prompt.md` says "auto-fix all Critical and High findings". On a client repo prefer "propose a patch" so nothing is edited without review.
- `chat-history.prompt.md` writes prompts and decisions into the codebase. Make it opt-in per project; on client repos that log ends up in their git history.
- `project-development.prompt.md` defaults to SQLite; every real project here runs Postgres or Supabase.
- `Planning-Document-Checklist.txt` is the list of planning and operations documents that `project-development` expects to find before it builds.
- The raw-source workbook (`all-prompts-compact`, 17 Apr 2026) was deleted on 9 Sep 2026 and stays in git history at commit 2eca7e0. Edit the `.md` files; there is no workbook to keep in sync.
