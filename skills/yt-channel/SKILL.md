---
name: yt-channel
description: Use when you want to study a whole YouTube channel — inventory every video, download transcripts, summarize each, and distill a master insights doc. For analyzing a competitor, creator, or framework author. Triggers on "/yt-channel", "analyze the channel of X", "study X on youtube", "inventory channel <URL>".
---

# Skill: yt-channel

Full pipeline: from `https://www.youtube.com/@creator` to a strategic `INSIGHTS.md`, via inventory → transcripts → per-video summaries. Output under `outputs/research/youtube/{creator-slug}/`. Free (yt-dlp local + your tokens for the summaries).

## Triggers
- `/yt-channel` · `/yt-channel @creator`
- "analyze the youtube channel of <creator>" / "inventory the channel <URL>" / "study <competitor> on youtube"

## Prerequisite
- `yt-dlp` in PATH (`brew install yt-dlp`). Runs where bash is your real shell (e.g. Claude Code in a terminal).

## Filesystem
```
outputs/research/youtube/{creator-slug}/
├── inventory.md                     # categorized by priority
├── selected-video-ids.txt
├── transcripts/
│   ├── {YYYYMMDD}_{videoID}_{title}.{it,en}.vtt
│   └── txt/{YYYYMMDD}_{videoID}_{title}.txt
├── summaries/{YYYYMMDD}_{videoID}.md
└── INSIGHTS.md
```

## Workflow
1. **Inputs**: channel URL/handle; a kebab-case `slug` (default from handle, confirm); subtitle langs (default `it,en` — set to your language(s)).
2. **Inventory** — list every video (metadata only):
   ```bash
   mkdir -p outputs/research/youtube/{slug} && cd outputs/research/youtube/{slug}
   yt-dlp --flat-playlist \
     --print "%(upload_date)s|%(view_count)s|%(duration)s|%(id)s|%(title)s" \
     "https://www.youtube.com/@{handle}/videos" > inventory-raw.txt
   ```
3. **Categorize** into `inventory.md` by priority: 🟢 HIGH (transcribe), 🟡 MED, 🔴 LOW (perishable/tech), ⚫ SKIP. Group by theme (strategy, case studies, framework, tutorials, news…). Add a "proposed selection" summary (count + minutes).
4. **Confirm selection** with the user, then save chosen URLs to `selected-video-ids.txt` (one `https://www.youtube.com/watch?v={id}` per line).
5. **Download subtitles**:
   ```bash
   cd transcripts
   yt-dlp --skip-download --write-auto-sub --sub-lang it,en --sub-format vtt \
     --output "%(upload_date)s_%(id)s_%(title)s.%(ext)s" \
     --batch-file ../selected-video-ids.txt 2>&1 | tee download.log
   ```
6. **Clean VTT → txt** (auto-subs have rolling duplicates):
   ```bash
   mkdir -p txt && python3 - <<'PY'
   import re
   from pathlib import Path
   TS=re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->"); INLINE=re.compile(r"<\d{2}:\d{2}:\d{2}\.\d{3}>|</?c>"); HTML=re.compile(r"<[^>]+>")
   src=Path("."); out=src/"txt"; out.mkdir(exist_ok=True)
   for vtt in (sorted(src.glob("*.it.vtt")) or sorted(src.glob("*.en.vtt"))):
       last=""; lines=[]
       for raw in vtt.read_text(encoding="utf-8",errors="replace").splitlines():
           l=raw.strip()
           if not l or l.startswith(("WEBVTT","Kind:","Language:")) or TS.match(l): continue
           t=HTML.sub("",INLINE.sub("",l)).strip()
           if not t or t==last or (last and t in last): continue
           lines.append(t); last=t
       (out/(vtt.stem.replace(".it","").replace(".en","")+".txt")).write_text("\n".join(lines),encoding="utf-8")
   print("done")
   PY
   ```
7. **Per-video summaries** — for each `.txt`, write `summaries/{YYYYMMDD}_{videoID}.md`. These are **strategic extracts, not retellings**: thesis, the relevant sections (case study / framework / numbers), every number stated, offer signals (CTAs, prices), and "notes for you" (what to copy, avoid, differentiate). 60-150 lines.
8. **Master `INSIGHTS.md`** when ≥10 summaries exist: positioning over time, public numbers, product/service catalog, ICP & verticals, recurring stack, proprietary framework, lessons for you.

## Notes
- Prefer your language's subtitle; fall back to `.en.vtt` (flag auto-translated transcripts as lower quality).
- Auto-subs have no punctuation — read them as a stream.
- Big channels (100+ videos): select aggressively (🟢-only). Main cost is your tokens for summaries.
- For specific videos (not a whole channel), use `/yt-video`.
