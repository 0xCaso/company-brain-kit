# company-brain

A **company brain** is your business as a structured markdown repo that an AI agent can actually run.

Think of your dad's garage: a few labelled compartments for your stuff, a pegboard of tools, and one person who knows where everything is and what the rules are.

- **`context/`** — your reference material: who you are, how you work, your brand. *(the drawers)*
- **`outputs/`** — what gets generated: drafts, lists, logs, research. *(the finished shelf)*
- **`CLAUDE.md`** — the rulebook + map that briefs whoever walks in. *(your dad)*
- **`.claude/skills/`** — your custom commands. *(the tools on the pegboard)*

Swap the operator — [Claude Code](https://claude.com/claude-code) today, [Hermes](https://hermes-agent.nousresearch.com/docs) tomorrow, a teammate next week — and the structure stays. That's the whole idea.

## How this repo is organized

This repo is a **kit**, not a brain itself. The skills live in `skills/` so you can browse them as plain folders. Claude Code loads skills from `.claude/skills/`, so to *use* one you copy it there.

```
skills/
├── init-company-brain/     ★ the guided scaffolder (+ templates/)
├── new-targets/  enrich/   example agentcash skills
└── yt-channel/   yt-video/ example research skills
scripts/
└── enrich-companies.py     the enrich pipeline as a CLI
```

## Quick start

1. Copy the scaffolder into a skills folder:
   ```bash
   cp -r skills/init-company-brain ~/.claude/skills/          # available everywhere
   # or, just for one project:
   cp -r skills/init-company-brain /path/to/project/.claude/skills/
   ```
2. In [Claude Code](https://claude.com/claude-code), run:
   ```
   /init-company-brain
   ```
3. Answer a few questions (all optional). You get a ready-to-use brain.

Do the same with any example skill you want (`cp -r skills/enrich ~/.claude/skills/`).

## The scaffolder ★
- **`init-company-brain`** — guided creation of a new brain. It interviews you (name, purpose, branding, areas of work) and writes `context/`, `outputs/`, `CLAUDE.md`, `README.md`. `projects/` is optional.

## Example skills — copy & adapt
- **`new-targets`** — source businesses by geography + segment via Google Maps, paid per call with [agentcash](https://agentcash.dev) (no API keys). → a target list.
- **`enrich`** — add phone / website / rating / headcount / decision-maker to a list (agentcash: Google Maps + Apollo + Firecrawl).
- **`yt-channel`** — ingest a whole YouTube channel: inventory → transcripts (`yt-dlp`) → per-video summaries → a master `INSIGHTS.md`.
- **`yt-video`** — same pipeline, for one or more specific videos.
- **`scripts/enrich-companies.py`** — the enrichment pipeline as a standalone CLI (via the `tempo` wallet).

## Companion skills worth installing (not bundled here)
- **[handoff](https://github.com/mattpocock/skills)** by Matt Pocock — compresses a long session into a handoff doc a fresh agent can pick up.
- **grill-me** — interviews you relentlessly to stress-test a plan or design until it holds.

## The stack it assumes
- **[Claude Code](https://claude.com/claude-code)** — the harness that operates the brain.
- **[agentcash](https://agentcash.dev)** — pay-per-call APIs (x402 / MPP), one wallet, zero API keys. Powers the research skills.
- **[Hermes](https://hermes-agent.nousresearch.com/docs)** — run the same brain outside the terminal (Telegram / Discord), so a whole team can use it at once.

Plain markdown + git. No database, no SaaS lock-in.

---
Built by Matteo Casonato · [rialto-ai.com](https://rialto-ai.com)
