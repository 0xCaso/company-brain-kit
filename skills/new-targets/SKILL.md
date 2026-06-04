---
name: new-targets
description: Use when you need to source a batch of business leads / prospects for a given geography and segment — building a target list from Google Maps. Triggers on "/new-targets", "find prospects in <area>", "source companies for <segment>", "build a target list".
---

# Skill: new-targets

Sources business candidates for a geography + segment via Google Maps text-search (paid per call with [agentcash](https://agentcash.dev)) and compiles them into a target list at `outputs/targets/[YYYY]-w[N]-target-list.md`.

## Triggers
- `/new-targets`
- "find prospects in <area>" / "source companies for <segment>" / "build a target list"

## Prerequisites
- An [agentcash](https://agentcash.dev) wallet with a small balance (~$0.02 per search call).
- The agentcash MCP (`mcp__agentcash__fetch`), or the `tempo` CLI.

## Workflow
1. **Gather inputs** (ask if not given): geographic area (city/region + radius), segment(s), volume (default 60-80), ISO week (default current).
2. **Read your own ICP** if you keep one in `context/` — to confirm segment definitions and which patterns are *anti-targets* (franchises, branches of multinationals, etc.) to filter out.
3. **Design queries**: 3-5 Google Maps text-search queries per segment, varying terms and towns. E.g. for "dental studios": `"dental studio <town A>"`, `"dental studio <town B>"`.
4. **Run searches** via `mcp__agentcash__fetch`:
   - URL: `https://stableenrich.dev/api/google-maps/text-search/partial`
   - Method: POST · Body: `{"textQuery": "<query>"}`
   - ~$0.02 / call. Estimate the total and confirm with the user if it exceeds ~$1.
5. **Compile**: de-duplicate by `place_id`; filter anti-targets; for each company write a one-line, **specific** pain hypothesis from observable signals (type, area, name).
6. **Write** `outputs/targets/[YYYY]-w[N]-target-list.md`: header (geography, volume, cost) + a markdown table per segment (include `place_id`) + an explicit anti-targets section.
7. **Suggest next step**: run `/enrich` to add phone + website + rating before outreach.

## Cost
- ~15-20 search calls × $0.02 = **$0.30-$0.40**.

## Notes
- Pain hypotheses should be specific to the segment + visible signals, not generic ("appointment reminders + pre-visit intake" beats "automation").
- ISO week: `date +%V`, or Python `datetime.date(Y,M,D).isocalendar()`.
- The output file is the input for `/enrich`.
