---
name: cartoon
description: Make a kids' cartoon of any length (one 1-minute story, a 5–10 minute episode, or a full hour of bedtime stories) built entirely in code. Felt-and-paper look, narration, music and sound effects, rendered on your own computer with HyperFrames. Use when the user asks for a kids' story video, a cartoon, a bedtime story, a long-form YouTube kids' video, or "make it like the Paper Rocket".
---

# CARTOON: kids' cartoons built in code

You write the story, draw every scene as SVG in code (felt and paper look), time every scene to the narration, add music and sound, and render an MP4. Nothing comes from a video generator, so there are no video credits and no watermark. The starter project in `kit/` is a finished 37-second film ("The Paper Rocket"). Copy it for every new story.

## What you need
- **Claude Code** (this skill runs in a terminal project folder).
- **Node 22+ and ffmpeg.** HyperFrames renders with `npx hyperframes`; nothing else to install.
- **A narration MP3.** The user generates it in ElevenLabs (see `references/narration.md`), or you use their API key if they give you one.
- **Python 3 + numpy** for the music synth (`kit/audio/groove.py`) and the mix (`kit/audio/mix.py`).

## The workflow (one story = one project folder)
Always show the user each plan and wait for an OK before building. Never skip a gate.

1. **Brief.** Ask: the idea in one line, the length (1 story ≈ 40–90 s · an episode ≈ 5–10 min · an hour = 8–12 stories, see `references/long-form.md`), the mood (bright and bouncy, or calm bedtime), and the age (2–4, 4–6, 6–8).
2. **Story.** Write it with `references/story-rules.md`: one small hero with one want, a gentle problem, friends help, a warm ending line. Bedtime: 60–70 words per minute of film; bright: 90–110.
3. **Scene plan.** Make a table with one row per sentence: SPOKEN (the exact narration), TEXT (the same words, appearing in the scene), VISUAL (what moves). Each scene runs 1.5–4 s for a bright story and 3–6 s for bedtime. Get the user's OK.
4. **Narration.** Give the user the script with ElevenLabs Eleven v4 audio tags (`references/narration.md`). Ask for 2 takes and keep the clearer one. Get word timings: `python3 src/words.py narration.mp3` (Whisper, one-time `pip install faster-whisper`) writes `src/words.json` (`[{"w": "Once", "t": 0.31}, …]`) and prints every word with its index. Fix any misheard words by hand, but keep the times.
5. **Build.** Copy `kit/` to a new folder. In `src/film.src.html`:
   - Set `SPANS`: one `[firstWordIndex, lastWordIndex]` per scene, in story order. Do the same in `src/build.py`, and set `TOTAL` there too.
   - Keep the helper kit (filters, `felt`, `paper`, `cloud`, `hills`, `words`, `popWords`, `push`, `shake`, `wobble`, scallop wipes). Delete the Paper Rocket scenes and write one block per scene with `scene("sN")`. Pop the story words in with `words()` + `popWords()`. Make characters with a `make<Name>()` builder like `makePip` (see `references/scene-kit.md`).
   - Every scene moves: a camera push, at least one character action, and one ambient loop (clouds, waves, stars, leaves).
   - Run `python3 src/build.py` to write `film/index.html` with the word times baked in.
6. **Check.** In `film/`: `npx hyperframes lint`, then `npx hyperframes snapshot --at <one time per scene>`. Look at every frame. Fix overlaps, words off-screen, characters cut off, and empty frames. Repeat until it's clean.
7. **Sound.** Write the music: `kit/audio/groove.py` is a marimba groove synthesized from scratch, with hits on the story beats. Change the tempo, the key and the hit marks. Mix it all with `python3 audio/mix.py narration.mp3 --dur <TOTAL> --music audio/groove.wav --sfx boing.mp3@12.4 …` into `film/assets/mix.wav` (steady voice, music ducked under it). Sound effects: the user's own library, or ElevenLabs sound effects.
8. **Render.** In `film/`: `npx hyperframes render -o ../renders/<name>.mp4 --quality standard`. Felt filters are heavy (~25 s of render per second of film on a laptop). Render drafts at `--quality draft` while iterating.
9. **Changes.** "Make scene 4 night-time": change only that scene's block (sky gradient, stars, lights on), re-snapshot that scene and re-render. Don't touch the other scenes.

## Long videos
For anything over ~3 minutes, read `references/long-form.md`: one project per story or chapter, render each, then join them with ffmpeg and write YouTube chapters.

## Rules
- **Original stories only.** No existing characters, brands or songs. Each episode needs its own story, not the same plot with new names (see `references/youtube.md`, YouTube's "inauthentic content" rule).
- **Kid-safe.** No scary peril for under-4s, no unsafe behaviour to copy, a kind resolution.
- **On-screen words = the narration**, the same words in the same order.
- **Deterministic.** Seeded random only (the kit's `rnd()`). Never `Math.random()`, `Date.now()` or real timers. Everything lives on the paused GSAP timeline.
- **Never play() or seek media in code.** HyperFrames owns playback.

## Files
- `kit/` is the starter film: `src/film.src.html` (helpers + 16 scenes + end card), `src/build.py`, `src/words.json`, `film/` (HyperFrames project, fonts), `audio/groove.py`, `audio/mix.py`.
- `references/story-rules.md`: how to write stories kids want to hear twice.
- `references/scene-kit.md`: every helper in the kit and how to build a new character.
- `references/narration.md`: voices, Eleven v4 tags, takes, word timings.
- `references/long-form.md`: the one-hour plan, render times, joining chapters.
- `references/youtube.md`: the upload checklist (made-for-kids, AI label, chapters, monetization rules).
- `examples/`: 5 real story scripts with scene plans. 01 is the film in `kit/`. 02–05 were first made with other looks (Blender felt dioramas, illustrated plates); their stories and scene plans work in the code kit too, with night palettes and glowing felt.
