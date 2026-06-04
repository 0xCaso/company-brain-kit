# scripts

Standalone helpers that run outside Claude Code.

## `enrich-companies.py`
The `/enrich` pipeline as a CLI — enrich a CSV of companies with phone, website, rating, headcount, and a likely decision-maker, via [stableenrich.dev](https://stableenrich.dev) paid per call.

**Requires:** the [`tempo`](https://agentcash.dev) CLI in PATH + a funded wallet (`~/.agentcash/wallet.json`).

```bash
# stage 1 — phone + website + rating (needs a place_id column)
python enrich-companies.py input.csv --stage place_details --output enriched-1.csv

# stage 2 — headcount + founded year + revenue (top 50 rows with a website)
python enrich-companies.py enriched-1.csv --stage apollo_enrich --top 50 --output enriched-2.csv

# stage 3 — decision-maker (top 20)
python enrich-companies.py enriched-2.csv --stage people --top 20 --output enriched-3.csv
```

Inside Claude Code, prefer the `/enrich` skill (interactive, adds the Firecrawl stage).
