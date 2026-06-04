---
name: init-company-brain
description: Use when someone wants to start a new company brain or AI workspace from scratch — scaffolding a structured markdown repo (context/ + outputs/ + CLAUDE.md) that an agent can operate. Triggers on "/init-company-brain", "create a company brain", "set up an AI workspace", "scaffold a brain", "new brain for <org>".
---

# Skill: init-company-brain

Scaffolds a new **company brain**: a structured markdown workspace plus a `CLAUDE.md` that briefs any agent on how to use it. The creation is **guided** — interview the user first, then write the files. Every question is optional; the user can skip a field or add things you didn't ask.

## Triggers
- `/init-company-brain`
- "create a company brain" / "scaffold a brain" / "set up an AI workspace"
- "new brain for <org>"

## What a company brain is (explain if the user is new to the idea)
A business as a git repo of plain markdown that an AI agent can run:
- `context/` — evergreen reference (who you are, how you work, brand). Read first.
- `outputs/` — generated / dated artifacts (drafts, lists, logs, research).
- `CLAUDE.md` — the rulebook + map, read at the start of every session.
- `.claude/skills/` — custom commands.

Swap the operator (Claude Code, Hermes, a teammate); the structure stays.

## Workflow

### 1. Guided interview — a couple of questions at a time
Run a short, friendly back-and-forth. **Tell the user every field is optional** ("skip" is fine, and they can add anything you didn't ask). Don't dump all questions at once; ask 1-2, listen, adapt.

1. **Name & slug** — what's it called? Derive a kebab-case slug and confirm.
2. **Purpose** — in 1-2 lines, what does this org do / what is this brain for?
3. **Operator & voice** — solo founder, or a team? First person or "we"?
4. **Areas of work** — the main domains (used to seed `context/` subfolders, e.g. `brand/`, `operations/`).
5. **Branding** *(optional)* — palette, fonts, tone of voice, do/don'ts.
6. **Memory** — want `context/decisions.md` (append-only strategy log) + an `outputs/log/` activity log? *(default: yes)*
7. **Projects** — per-client / per-engagement work? If yes, add `projects/` (one folder per engagement). **Default: NO** — add only if asked.

If the user says "just use defaults / go", proceed with: sensible names, memory on, no `projects/`.

### 2. Confirm the plan
Echo a one-paragraph summary (name, purpose, which folders, branding y/n, projects y/n). Get a quick OK before writing anything.

### 3. Write the scaffold
In the target directory (ask where; default: a new folder named after the slug):

```
<slug>/
├── CLAUDE.md          # from templates/CLAUDE.md.template, filled in
├── README.md          # from templates/README.md.template, filled in
├── context/
│   ├── <area>/         # one subfolder per area of work (if given)
│   └── decisions.md    # if memory on
└── outputs/
    └── log/            # if memory on
[└── projects/]         # only if requested
```

- Read [`templates/CLAUDE.md.template`](templates/CLAUDE.md.template) and [`templates/README.md.template`](templates/README.md.template). Replace the `{{PLACEHOLDERS}}` with the interview answers, and **remove** the optional blocks the user declined (branding, tone, memory rule, projects).
- Keep it minimal. Empty folders get a one-line `README.md` or a `.gitkeep` — don't auto-generate fake content.

### 4. Wrap up
- Offer to run `cd <slug> && git init`.
- Point the next moves: drop reference material into `context/`, copy skills into `.claude/skills/` (the sibling example skills in this repo are a starting point), then just open the folder in Claude Code.

## Notes
- **The heart is `CLAUDE.md`** — it encodes the *modus operandi* so any agent behaves consistently. Don't skimp on it; skimp on everything else.
- **Don't invent the org's details.** If the user skips a field, leave that section generic or omit it — never fabricate a mission, a brand, or facts.
- It's a starting point, not a cage. Tell the user to edit `CLAUDE.md` as their way of working gets clearer.
