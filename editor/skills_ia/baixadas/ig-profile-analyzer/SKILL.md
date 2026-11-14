---
name: ig-profile-analyzer
description: >-
  Use when the user wants a FULL data pull + performance analysis of one Instagram
  profile — every post, view counts (plays) for reels, likes, comments, dates, captions,
  post count, posting structure/cadence, and a ranking of which videos/posts performed
  best. Triggers: "puxar todos os dados do perfil", "quais vídeos deram mais views",
  "analisa esse perfil do Instagram", "quantas postagens", "estrutura de conteúdo",
  "analyze this IG profile", "which reels performed best", "dump all posts from @handle".
  For single searches, hashtags, DMs, comments or stories use instagram-search instead.
---

# Instagram Profile Analyzer

Dump a profile's ENTIRE post history (with real reel view counts) through the user's
logged-in Chrome session, then run a local zero-token analysis: top performers, format
breakdown, cadence, best posting hours, caption patterns.

**REQUIRED BACKGROUND:** instagram-search skill — its Prerequisites (Chrome MCP
connected, user signed in, tab on instagram.com) and Constraints (45 s JS timeout,
never return base64/cursor strings, 250-400 ms sleeps, 429 backoff) apply verbatim
here. Do those checks first. Do NOT re-explain them; just run them.

## When NOT to use

- One-off profile stats ("quantos seguidores tem @X") → instagram-search workflow 10.
- Hashtag / keyword / DM / location / audio / comments → instagram-search.
- The user's OWN account insights (reach, saves, watch time, demographics) —
  unobtainable for third-party profiles; only public counters exist. Say so upfront.

## Workflow

1. **Prereq checks** (from instagram-search). Navigate the Chrome tab to
   `https://www.instagram.com/{username}/`.
2. **Inject** `scripts/dump_profile.js` via `javascript_tool` (once per tab).
3. **Init:** `await IGProf.init('username')` → returns `{uid, posts, followers, is_private}`.
   - `is_private` and not followed → stop, tell user.
   - `posts > 500` → tell the user the estimated time (~40 posts/min incl. sleeps) and
     offer to cap at the most recent N. Proceed with full pull if they asked for "tudo".
4. **Feed loop:** call `await IGProf.feedPage()` repeatedly (each call = 4 pages ≈ 130
   posts, safely under the 45 s timeout). It returns `{collected, total, more}`. Repeat
   until `more === false`. State lives on `window.__igProf` — if the user navigates
   away, it restarts from zero, so tell them to leave the tab alone.
5. **Reels backfill:** `await IGProf.clipsPage()` repeatedly until `{more: false}`.
   Merges `ig_play_count` into rows by `pk` — the feed endpoint omits plays on some
   reels; `/api/v1/clips/user/` is authoritative for views.
6. **Export:** `await IGProf.dump(offset, 200)` in chunks; append each chunk as JSON
   lines to `posts.jsonl` in the working folder. Captions come pre-sliced to 600 chars
   (content-filter safe). Never return cursors or raw items.
7. **Completeness check:** compare row count vs `posts` from init. Short by >3%? A 429
   probably hit mid-loop — resume `feedPage()` (cursor is still cached) instead of
   restarting.
8. **Analyze:** `python scripts/analisar_perfil.py posts.jsonl <followers>` — pure
   stdlib (no pandas, no installs; global Python must stay untouched). Writes
   `analise.md` + `posts.csv` next to the JSONL.
9. **Deliver:** summary in chat (top 10 by views WITH post URLs, format split, cadence,
   best hours, overperformer insights) + full absolute paths of `analise.md`,
   `posts.csv`, `posts.jsonl`.

## Fields per post (what dump() returns)

`pk, code` (URL = `instagram.com/p/{code}/` or `/reel/{code}/` when product_type=clips),
`taken_at` (unix), `media_type` (1 img / 2 video / 8 carousel), `product_type`
(`clips` = reel — identify reels by THIS, not media_type), `like_count`,
`comment_count`, `plays` (= `ig_play_count` || `play_count`, reels only), `view_count`
(non-reel video), `likes_hidden` (`like_and_view_counts_disabled` — record null, not
zero), `caption` (≤600 chars), `video_duration`, `carousel_count`, `coauthors`,
`location`.

## Analysis rules (what the script encodes — don't hand-roll)

- **Views ranking = `plays` for reels, `view_count` for other video.** Likes rank is
  separate. Never mix.
- **Median + P90, never mean** — big accounts have extreme outliers.
- **Overperformance = z-score vs trailing 20-post window**, not absolute counts:
  absolute likes across years measure follower growth, not content quality.
- **Sort by `taken_at`, not array order** — pinned posts arrive first out of order.
- **Coauthored posts flagged** — collab reach inflates numbers vs solo posts.
- Cadence: posts/month series, gap distribution, longest silence.
- Caption patterns of top-decile posts: length bucket, hashtag count, has-CTA.

## Failure modes

| Symptom | Fix |
|---|---|
| Feed returns rows but `plays` null on reels | Run clipsPage() backfill (step 5) — not a bug |
| Row count < profile post count | Resume feedPage(); archived posts also shrink the diff |
| 401/403 mid-pull | Session expired — user refreshes tab, cursor cache survives if same tab |
| `[BLOCKED: ...]` in dump return | Chunk smaller (dump offset,100); captions already sliced |
| JS timeout | Never loop >4 feed pages / >6 clips pages per call |
| Duplicate rows | Dedup by `pk` (dump already does; re-check after resume) |

## Red flags — stop and re-read Workflow

- Writing a fresh pagination loop instead of injecting `scripts/dump_profile.js`
- Ranking reels by `like_count` because plays "were missing" → backfill first
- Returning cursors/raw items from JS "just to debug"
- Installing pandas/instaloader in the global Python
- Declaring "pronto" without the completeness check (step 7)
