"""src.html + words.json → index.html (word timings injected, scene clip timings written statically)."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "..", "film")
W = json.load(open(os.path.join(HERE, "words.json")))
SPANS = [[0, 3], [4, 8], [9, 13], [14, 18], [19, 24], [25, 27], [28, 29], [30, 33], [34, 38], [39, 41],
         [42, 45], [46, 49], [50, 57], [58, 62], [63, 70], [71, 86]]
TOTAL = 37.0
START = [0.0] + [round(W[a]["t"] - 0.16, 3) for a, _ in SPANS[1:]]
END = START[1:] + [TOTAL]
src = open(os.path.join(HERE, "film.src.html")).read().replace("__WORDS__", json.dumps(W))
for i, (s, e) in enumerate(zip(START, END), start=1):
    src = re.sub(rf'(<div class="scene clip" id="s{i}") data-start="[^"]*" data-duration="[^"]*"',
                 rf'\1 data-start="{s}" data-duration="{round(e - s, 3)}"', src)
open(os.path.join(FILM, "index.html"), "w").write(src)
for i, (s, e) in enumerate(zip(START, END), start=1):
    print(f"s{i:<3} {s:6.2f} → {e:6.2f}  ({e - s:4.2f}s)")
