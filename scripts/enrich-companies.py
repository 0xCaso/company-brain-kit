#!/usr/bin/env python3
"""enrich-companies.py — Enrich a company list via stableenrich.dev APIs.

Three-stage pipeline using x402/MPP micropayments via the `tempo` CLI (agentcash
wallet at ~/.agentcash/wallet.json):

  stage 1  place_details   per place_id: GET google-maps/place-details/full   ~$0.05 each
  stage 2  apollo_enrich   per row with website: POST apollo/org-enrich        ~$0.05 each
  stage 3  people          top-N rows: POST apollo/people-search for DM titles ~$0.02 each

  Note: place-details/partial ($0.02) does NOT return phone/website — use /full.

Usage:
    python enrich-companies.py input.csv --stage place_details --output enriched-1.csv
    python enrich-companies.py enriched-1.csv --stage apollo_enrich --top 50 --output enriched-2.csv
    python enrich-companies.py enriched-2.csv --stage people --top 20 --output enriched-3.csv

Input CSV needs a `place_id` column for stage 1, and a `website` column for stages 2-3.
Output preserves all input columns and adds the enrichment fields.

Requires the `tempo` CLI in PATH and a funded wallet (see https://agentcash.dev).
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse


STABLEENRICH = "https://stableenrich.dev"
RATE_LIMIT_SECONDS = 0.2  # gentle pause between calls

# Decision-maker titles for people-search. Add localized titles for your market.
DM_TITLES = ["CEO", "Owner", "Founder", "President", "Managing Director", "Director", "Partner"]


def tempo_request(url: str, method: str = "GET", body: dict | None = None) -> dict:
    """Call a stableenrich endpoint via the tempo CLI. Returns parsed JSON.

    Raises RuntimeError if the CLI exits non-zero.
    """
    cmd = ["tempo", "request", "--url", url, "--method", method]
    if body is not None:
        cmd.extend(["--body", json.dumps(body)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"tempo request failed ({result.returncode}): {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"tempo response not JSON: {e}\n{result.stdout[:500]}")


def domain_from_url(url: str) -> str:
    """Extract the bare domain from a website URL (strip scheme, www, path)."""
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = parsed.netloc or parsed.path
    return host.lstrip("www.").split("/")[0]


def stage_place_details(rows: list[dict]) -> list[dict]:
    """For each row with a place_id, fetch place-details/full and merge fields."""
    out = []
    for i, row in enumerate(rows, 1):
        place_id = row.get("place_id", "").strip()
        name = row.get("name", "unknown")
        if not place_id:
            print(f"[{i}/{len(rows)}] SKIP (no place_id): {name}", file=sys.stderr)
            out.append(row)
            continue
        url = (
            f"{STABLEENRICH}/api/google-maps/place-details/full"
            f"?placeId={place_id}&excludeFields=photos,reviews,accessibilityOptions,parkingOptions,paymentOptions"
        )
        try:
            data = tempo_request(url, method="GET")
        except Exception as e:
            print(f"[{i}/{len(rows)}] ERROR: {name} -- {e}", file=sys.stderr)
            out.append(row)
            continue
        row["phone"] = data.get("nationalPhoneNumber", "")
        row["phone_intl"] = data.get("internationalPhoneNumber", "")
        row["website"] = data.get("websiteUri", "")
        row["address"] = data.get("formattedAddress", row.get("address", ""))
        row["rating"] = data.get("rating", "")
        row["user_rating_count"] = data.get("userRatingCount", "")
        row["primary_type"] = data.get("primaryType", "")
        row["google_maps_uri"] = data.get("googleMapsUri", "")
        row["business_status"] = data.get("businessStatus", "")
        out.append(row)
        print(
            f"[{i}/{len(rows)}] OK: {name} | phone={row['phone'] or 'n/a'} "
            f"site={row['website'] or 'n/a'} rating={row['rating']}({row['user_rating_count']})",
            file=sys.stderr,
        )
        time.sleep(RATE_LIMIT_SECONDS)
    return out


def stage_apollo_enrich(rows: list[dict], top_n: int | None = None) -> list[dict]:
    """For each row with a website, call Apollo org-enrich and merge company info."""
    candidates = [r for r in rows if r.get("website")]
    if top_n is not None:
        candidates = candidates[:top_n]
    target_indexes = {id(r) for r in candidates}
    out = []
    processed = 0
    for row in rows:
        if id(row) not in target_indexes:
            out.append(row)
            continue
        processed += 1
        domain = domain_from_url(row.get("website", ""))
        name = row.get("name", "unknown")
        if not domain:
            out.append(row)
            continue
        url = f"{STABLEENRICH}/api/apollo/org-enrich"
        try:
            data = tempo_request(url, method="POST", body={"domain": domain})
        except Exception as e:
            print(f"[{processed}/{len(candidates)}] ERROR: {name} -- {e}", file=sys.stderr)
            out.append(row)
            continue
        org = data.get("organization", data)
        row["headcount"] = org.get("estimated_num_employees", "")
        row["linkedin_url"] = org.get("linkedin_url", "")
        row["founded_year"] = org.get("founded_year", "")
        row["revenue"] = org.get("organization_revenue_printed", "")
        row["industry"] = org.get("industry", "")
        out.append(row)
        print(
            f"[{processed}/{len(candidates)}] OK: {name} | headcount={row['headcount']} "
            f"founded={row['founded_year']}",
            file=sys.stderr,
        )
        time.sleep(RATE_LIMIT_SECONDS)
    return out


def stage_people(rows: list[dict], top_n: int = 20) -> list[dict]:
    """For top-N rows with a website, find a likely decision-maker via Apollo people-search."""
    candidates = [r for r in rows if r.get("website")][:top_n]
    target_indexes = {id(r) for r in candidates}
    out = []
    processed = 0
    for row in rows:
        if id(row) not in target_indexes:
            out.append(row)
            continue
        processed += 1
        domain = domain_from_url(row.get("website", ""))
        name = row.get("name", "unknown")
        if not domain:
            out.append(row)
            continue
        url = f"{STABLEENRICH}/api/apollo/people-search"
        body = {"q_organization_domains": [domain], "person_titles": DM_TITLES, "per_page": 5}
        try:
            data = tempo_request(url, method="POST", body=body)
        except Exception as e:
            print(f"[{processed}/{len(candidates)}] ERROR: {name} -- {e}", file=sys.stderr)
            out.append(row)
            continue
        people = data.get("people") or data.get("contacts") or []
        if people:
            top = people[0]
            row["dm_name"] = top.get("name", "")
            row["dm_title"] = top.get("title", "")
            row["dm_linkedin"] = top.get("linkedin_url", "")
            row["dm_email"] = top.get("email", "")
        out.append(row)
        print(
            f"[{processed}/{len(candidates)}] OK: {name} | dm={row.get('dm_name', 'n/a')} "
            f"title={row.get('dm_title', 'n/a')}",
            file=sys.stderr,
        )
        time.sleep(RATE_LIMIT_SECONDS)
    return out


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    all_fields: set[str] = set()
    for r in rows:
        all_fields.update(r.keys())
    primary = [
        "name", "segment", "address", "phone", "website",
        "headcount", "rating", "user_rating_count", "founded_year",
        "dm_name", "dm_title", "dm_linkedin", "dm_email",
        "linkedin_url", "industry", "revenue", "primary_type",
        "google_maps_uri", "place_id", "pain_hypothesis", "notes",
    ]
    cols = [c for c in primary if c in all_fields]
    cols += sorted(all_fields - set(cols))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich a company list via stableenrich.dev")
    parser.add_argument("input", type=Path, help="Input CSV")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV")
    parser.add_argument(
        "--stage",
        choices=["place_details", "apollo_enrich", "people"],
        required=True,
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--top", type=int, default=None,
        help="For apollo_enrich/people: limit to top N rows with a website",
    )
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"Input file not found: {args.input}")

    rows = read_csv(args.input)
    print(f"Loaded {len(rows)} rows from {args.input}", file=sys.stderr)

    if args.stage == "place_details":
        enriched = stage_place_details(rows)
    elif args.stage == "apollo_enrich":
        enriched = stage_apollo_enrich(rows, top_n=args.top)
    elif args.stage == "people":
        enriched = stage_people(rows, top_n=args.top or 20)
    else:
        sys.exit(f"Unknown stage: {args.stage}")

    write_csv(args.output, enriched)
    print(f"Wrote {len(enriched)} rows to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
