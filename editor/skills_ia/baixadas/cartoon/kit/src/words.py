"""Narration MP3 -> src/words.json ([{"w": word, "t": start_seconds}, ...]) with Whisper word timings.
setup once:  pip install faster-whisper
usage:       python3 src/words.py narration.mp3"""
import json, os, sys
from faster_whisper import WhisperModel

segs, _ = WhisperModel("medium.en", device="cpu", compute_type="int8").transcribe(sys.argv[1], word_timestamps=True, beam_size=5)
words = []
for s in segs:
    for w in s.words:
        txt = w.word.strip()
        if words and txt[:1] in ",-" and txt[1:2].isalnum():   # Whisper splits "60,000" / "hour-long"; glue them back
            words[-1]["w"] += txt
        else:
            words.append({"w": txt, "t": round(w.start, 3)})
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.json")
json.dump(words, open(out, "w"), indent=1)
print(" ".join(f"{i}:{w['w']}" for i, w in enumerate(words)))
print(f"\n{len(words)} words -> {out}  (the numbers are the word indexes you use in SPANS)")
