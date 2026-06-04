---
name: yt-video
description: Use when someone shares one or more YouTube links and wants the gist / a strategic summary — extract transcripts and summarize each. Batch-native, even across different creators. Triggers on a youtube.com/watch or youtu.be URL plus "summarize / what does this say / extract insights".
---

# Skill: yt-video

Single/multi-video version of `/yt-channel`. From URL(s) → clean transcript + strategic summary each. Same filesystem layout, so it composes with `/yt-channel`. Free (yt-dlp local + your tokens).

## Triggers
- `/yt-video <URL> [<URL> ...]` (batch supported)
- "summarize this video <URL>" / "extract the insights from <URL1> <URL2>"
- one or more YouTube URLs + "watch this / interesting"

## Prerequisite
- `yt-dlp` in PATH (`brew install yt-dlp`).

## Filesystem
Identical to `/yt-channel`:
```
outputs/research/youtube/{creator-slug}/
├── transcripts/{YYYYMMDD}_{videoID}_{title}.{it,en}.vtt  →  txt/...txt
└── summaries/{YYYYMMDD}_{videoID}.md
```

## Workflow
1. **Resolve URLs + slug** — one batch call to map the uploader:
   `yt-dlp --print "%(id)s|%(uploader)s|%(channel_id)s" --skip-download <URL...>`.
   If the uploader matches an existing `outputs/research/youtube/{slug}/`, reuse it; else propose a slug and confirm. Different creators → separate folders.
2. **Download subtitles** (one call per slug — yt-dlp takes multiple URLs):
   ```bash
   mkdir -p outputs/research/youtube/{slug}/transcripts && cd outputs/research/youtube/{slug}/transcripts
   yt-dlp --skip-download --write-auto-sub --sub-lang it,en --sub-format vtt --no-overwrites \
     --output "%(upload_date)s_%(id)s_%(title)s.%(ext)s" "<URL1>" "<URL2>"
   ```
3. **Clean VTT → txt** — same filter as `/yt-channel` (drop timestamps, inline tags, rolling duplicates), restricted to the just-downloaded videoIDs.
4. **Summaries** — one per video (serial, not parallelized; each deserves attention). Template: thesis, relevant sections, every number stated, offer signals, "notes for you". 60-150 lines, a strategic extract not a retelling.
5. **Output in chat** — single video: file path + thesis + notes inline. Batch: a compact list, one link + one-line thesis each.

## Batch mode
Batch-native: N URLs in one invocation → run once, produce N summaries. Resolve + download are batched; summaries stay serial. Mixed-creator batches keep separate folders. Don't escalate to `/yt-channel` just for several links — that's only for inventorying a whole channel.

## Notes
- Prefer your language's subtitle; flag `.en` auto-translations as lower quality.
- Missing subtitles are rare on YouTube; if so, skip that video and report — no custom speech-to-text.
