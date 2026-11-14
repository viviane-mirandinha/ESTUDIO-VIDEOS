# Long-form: from one story to a full hour

Claude can keep going for as long as you want. A one-hour video is just many short films made the same way and joined. The work is in planning and rendering, not in any special tool.

## Pick a format
| Format | How it's built | Example |
|---|---|---|
| **Story collection** (easiest) | 8–12 separate stories of 4–7 minutes, one project each | "1 Hour of Calm Bedtime Stories: The Little Lights" |
| **Chapter story** | One long story split into 6–10 chapters, same characters | "Pip's Trip to the Moon: the whole adventure" |
| **Episode + compilation** | Publish single episodes (5–10 min) first, then a compilation of the best ones | Episodes 1–8 → "1 hour compilation" |

## The plan (write this first and show the user)
1. **Series bible**: the hero(es), their looks (one line each), the world, the narrator voice, the palette, the music style.
2. **Story list**: one line per story or chapter, each with its own problem and ending (never the same plot twice).
3. **Minutes per story** so the total lands on the target: 10 × 6 min = 60 min.
4. **Shared pieces**: the same intro card (5–8 s), the same "The End" card, and the same transitions between stories. YouTube allows a shared intro and outro as long as the stories differ.

## Build it
- One folder per story: copy `kit/` each time (`story-01/`, `story-02/` …). Characters live in a shared `characters.js` that every story loads, so Pip looks the same in all of them.
- Narrate each story separately (short files are easy to redo), and make `words.json` per story.
- Bedtime pacing: 3–6 s per scene, slow camera pushes, quiet ambient loops (waves, stars, leaves). Roughly 10–15 scenes per minute of film.

## Render time (be honest about it)
The felt-and-paper look is heavy: on a recent laptop it takes ~25 seconds of rendering per second of film at standard quality. So:
| Length | Render time (approx.) |
|---|---|
| 1 minute | ~25 minutes |
| 6-minute story | ~2.5 hours |
| 1 hour | ~25 hours (run it overnight, story by story) |

Ways to make it faster:
- Iterate at `--quality draft`, and render standard only once a story is approved.
- Fewer felt shapes per scene; plain SVG for star fields and grass.
- Render several stories in parallel on a strong machine, or with `npx hyperframes render --help` to see the cloud and Lambda options.

## Join the stories
```
# list.txt: one line per file, in order
file 'story-01/renders/film.mp4'
file 'story-02/renders/film.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy one-hour.mp4
```
All the stories must share the same size, frame rate and audio settings (they do if every one is built from `kit/`).

## Chapters for YouTube
Write the start time of each story in the description, starting with `00:00`:
```
00:00 The Lighthouse Mouse
05:42 Little Light
11:20 The Moon Path
```
Get the times by adding up the story lengths (`ffprobe -show_entries format=duration story-01/renders/film.mp4`). YouTube needs at least 3 chapters, the first at 00:00, each 10 seconds or longer.
