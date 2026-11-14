# Narration (ElevenLabs, model Eleven v4)

## Voice
Pick one narrator for the whole channel and never change it. Search these names in the ElevenLabs Voice Library:
| Voice | Sound | Best for |
|---|---|---|
| Katherine – Calm Luxury Narrator | British, soft, unhurried | Bedtime (our Lighthouse Mouse, Prickles, Little Light, Moon Path) |
| Beth – gentle and nurturing | British, motherly | Bedtime, toddlers |
| Holly – Engaging Children's Storyteller | American, cheerful, dramatic | Bright stories |
| Margot – Bright, friendly and upbeat | American, bright | Bright stories |
| Max Hepburn | British male, warm | Either |

## Audio tags
Eleven v4 reads [bracketed] directions as delivery, not as words. Put one at the start and one at each mood change:
- Bedtime: `[slowly, softly, a warm bedtime storyteller reading to a sleepy child]` … `[hushed]` … `[gently hopeful]` … `[warm, smiling]`
- Bright: `[bright, playful storyteller, lively pace]` … `[building suspense]` … `[shouting with joy]` … `[delighted]`
- Pauses: `[pause]`, `[long pause]`, or an ellipsis "…" in the text.

Example (bedtime):
```
[slowly, softly, a warm bedtime storyteller reading to a sleepy child] At the edge of the sea… stood a lighthouse. [pause] And a tiny mouse named Juniper… kept it shining.
```

## Takes
- Generate 2 takes of each story; keep the one with the clearest words and calmest pace.
- Don't time-stretch or cut words together. Re-generate instead.
- For long videos, narrate one story per generation, so each file stays short and easy to redo.

## Word timings (what syncs the scenes)
```
pip install faster-whisper      # once
python3 src/words.py narration.mp3
```
It writes `src/words.json` in the shape `[{"w": "Once", "t": 0.31}, …]` and prints each word with its index (the numbers you put in `SPANS`). Fix misheard names by hand ("Pip", not "Pep") but keep the times, then run `python3 src/build.py` again.

## Loudness
Mix the voice around −16 LUFS, with music 10–14 dB under it. `kit/audio/mix.py` does this with ffmpeg + numpy.
