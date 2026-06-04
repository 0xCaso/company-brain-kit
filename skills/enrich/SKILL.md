---
name: enrich
description: Use when you have a list of companies (with place_ids and/or websites) and want to add contact + firmographic data — phone, website, rating, headcount, decision-maker. Triggers on "/enrich", "enrich the target list", "add phone and website to <file>".
---

# Skill: enrich

Enriches a target list via [agentcash](https://agentcash.dev) (Google Maps + Apollo + Firecrawl). Four optional stages — pick which to run by budget. Mirrors `scripts/enrich-companies.py`.

## Triggers
- `/enrich`
- "enrich the target list" / "add phone and website to <file>"

## Prerequisites
- An agentcash wallet with balance; `mcp__agentcash__fetch` (or the `tempo` CLI).

## Workflow
1. **Find the file**: the path the user gave, else the latest `outputs/targets/*-target-list.md`. Parse the `place_id`s from the tables.
2. **Confirm stages + cost** (state the estimate before running):
   - **Stage 1 — `place-details/full`**: phone + website + rating. ~$0.05/company. *(all companies)*
   - **Stage 2 — `apollo/org-enrich`**: headcount + LinkedIn + founded year + revenue. ~$0.05/company. *(top 15-20)*
   - **Stage 3 — `apollo/people-search`**: decision-maker name + LinkedIn. ~$0.02/company. *(top 15-20)*
   - **Stage 4 — `firecrawl/scrape`**: refine pain hypothesis from the homepage. ~$0.013/company. *(top 10-15)*
3. **Stage 1** — for each `place_id`, GET
   `https://stableenrich.dev/api/google-maps/place-details/full?placeId=<id>&excludeFields=photos,reviews,regularOpeningHours,currentOpeningHours`.
   Extract `nationalPhoneNumber`, `websiteUri`, `rating`, `userRatingCount`, `businessStatus`. Batch 10-15 in parallel.
4. **Stage 2** — strip the domain from each website; POST `apollo/org-enrich` `{"domain":"<domain>"}`. Extract `estimated_num_employees`, `linkedin_url`, `founded_year`, `organization_revenue_printed`, `industry`.
5. **Stage 3** — POST `apollo/people-search` `{"q_organization_domains":["<domain>"],"person_titles":["CEO","Owner","Founder","Managing Director","Director"],"per_page":3}`. Take the top match: name, title, linkedin.
6. **Stage 4** — POST `firecrawl/scrape` `{"url":"<website>","formats":["markdown"]}`. From the markdown write a 5-bullet read (services, scale, decision-maker, ops stack, voice) + a refined pain hypothesis.
7. **Update the markdown in place**: add columns `Phone`, `Website`, `Rating (n)`, optionally `Headcount`, `Decision-maker`. Preserve existing notes.

## Cost reference
| Stage | API | / call | All 80 | Top 15 |
|---|---|---|---|---|
| 1 | google-maps/place-details/full | $0.05 | $4.00 | $0.75 |
| 2 | apollo/org-enrich | $0.05 | $4.00 | $0.75 |
| 3 | apollo/people-search | $0.02 | $1.60 | $0.30 |
| 4 | firecrawl/scrape | $0.013 | $1.04 | $0.20 |

## Notes
- **Use `place-details/full`, NOT `/partial`** — partial does not return phone or website.
- Apollo coverage for small/local businesses is patchy (~30-50%). Missing data ≠ small company.
- Firecrawl lands ~100% on homepages — the value is the markdown for refining pain, not discovery.
- For repeated batch runs outside Claude Code, use `scripts/enrich-companies.py`.
