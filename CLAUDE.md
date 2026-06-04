# company-brain-kit — agent guide

**You've been pointed at the company-brain-kit.** It's a *kit*, not a brain itself: a
guided scaffolder plus a few example skills someone can copy into their own setup.
Your job is to help the person who handed you this repo get value from it fast.

You may be working **just from this repo's URL** (no local clone) — that's fine. Read
each file you need via its raw URL as you go (e.g.
`https://raw.githubusercontent.com/0xCaso/company-brain-kit/main/skills/init-company-brain/SKILL.md`).
You don't need to clone anything to scaffold a brain or explain a skill; only offer to
clone if the user wants to keep the example skills on their machine.

## What's here
- `skills/init-company-brain/` — ★ the guided scaffolder. Its `SKILL.md` interviews the
  user and writes a new company brain (`context/`, `outputs/`, `CLAUDE.md`, `README.md`).
  Templates live in `skills/init-company-brain/templates/`.
- `skills/{new-targets,enrich,yt-channel,yt-video}/` — example skills (lead sourcing,
  enrichment, YouTube research). Generalized — meant to be copied and adapted.
- `scripts/enrich-companies.py` — the enrichment pipeline as a standalone CLI.
- `README.md` — the human-readable version of all this.

Skills sit in `skills/` as a browsable catalog. Claude Code only loads skills from
`.claude/skills/`, so to *run* one as a slash command you copy it there first.

## Start the session here
When someone opens this repo, don't wait for a detailed brief. Greet them in one line
and ask what they want to do — let them answer in their own words. Offer these paths:

1. **Init a company brain** — scaffold a new brain for their business.
2. **Walk me through a skill** — explain what a skill does and how to adapt it.
3. **Install a skill** — copy a skill into their `.claude/skills/` so they can use it.
4. **Just explain the kit** — a 30-second tour.

Then route:

### 1 · Init a company brain
Read `skills/init-company-brain/SKILL.md` and follow it exactly — it's a guided
interview. First ask **where** to create the brain (a new folder, *not* inside this
kit). Run the questions, then write the scaffold from the templates. Don't invent
answers; if you don't know, ask.

### 2 · Walk me through a skill
Ask which one (or suggest based on their goal). Read that `skills/<name>/SKILL.md` and
explain plainly: what it does, what it needs (e.g. an agentcash wallet, `yt-dlp`), the
trigger phrases, and how they'd adapt it to their own work.

### 3 · Install a skill
Copy the chosen skill into a skills folder, then tell them the slash command is live:
```bash
cp -r skills/<name> ~/.claude/skills/          # available everywhere
# or, just for one project:
cp -r skills/<name> /path/to/project/.claude/skills/
```
No local clone? Either clone the repo first, or recreate the skill by reading its files
via their raw URLs and writing them into `~/.claude/skills/<name>/`.

### 4 · Explain the kit
Give the 30-second tour from "What's here" above, then offer paths 1–3.

## Good to know
- The skills assume **[agentcash](https://agentcash.dev)** for paid APIs (pay per call,
  one wallet, no API keys) and **[Claude Code](https://claude.com/claude-code)** as the
  harness. `yt-channel` / `yt-video` also need `yt-dlp`.
- Everything is plain markdown + git. Nothing here phones home.
- Don't invent facts, numbers, or file contents — read the actual files before you
  describe them.
- Repo: https://github.com/0xCaso/company-brain-kit
