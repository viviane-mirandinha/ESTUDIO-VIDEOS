# The scene kit (kit/src/film.src.html)

Everything is SVG inside 1920×1080 scenes, animated on one paused GSAP timeline `tl`. The narration word times come in as `W = [{w, t}, …]`. `SPANS[i]` is the word range of scene i, `START[i]` / `END[i]` are its times in seconds.

## Materials (SVG filters in `#defs`)
- `url(#felt)`: fibre texture + soft edge + a little shadow. The look of every character and prop.
- `url(#paper)`: flat paper grain for cards, tape and wipes.
- `url(#bg)`: subtle grain on the sky gradient.
- `url(#glow)`: soft glow for stars, flames, lamps.

## Building blocks
| Helper | What it makes |
|---|---|
| `scene("sN")` | Returns `{host, svg, cam}`. Draw into `cam` (the camera group), put words on `host`. |
| `bgRect(cam, top, bottom)` | Sky/background gradient with grain. |
| `felt(parent, tag, attrs, fill, stitch=true, inset=0.9)` | Any SVG shape in felt, with a running stitch inset (pass `false` for no stitch, or a colour string for the stitch colour). |
| `paper(parent, tag, attrs, fill)` | The same shape in paper. |
| `bead(parent, x, y, r)` | Bead eye with a highlight. |
| `cloud(parent, x, y, w, h)` · `cloudPath()` | Puffy felt cloud. |
| `star5(cx, cy, ro)` | Star path (use with `felt` or `E("path")`). |
| `flower(parent, x, y, col)` | Felt flower; returns `{g, head}` so the head can wobble. |
| `hills(parent, y, col, amp, shift)` | Rolling felt hills. Stack 2–3 for depth. |
| `puff(parent, x, y, r)` | Smoke/dust puff. |
| `E(tag, attrs, parent)` · `G(parent, attrs)` | Raw SVG element / group. |
| `R(a, b)` | Seeded random number (deterministic). Never use `Math.random()`. |
| `C` | The palette (fox orange, grass greens, navy, card brown…). |

## Characters
`makePip(parent, x, y, scale, opts)` (the fox) and `makeRocket(...)` show the pattern. Copy it for every new character:
- The origin sits at the feet; the character is built from `felt` ellipses and paths, with `bead` eyes and felt cheeks.
- Return the parts you will animate as separate groups: `{g, inner, head, tail, arm, earL, earR}`.
- Rotate parts around a pivot with `svgOrigin: "x y"` **and** `smoothOrigin: false` (without it, groups jump hundreds of pixels).
- Pop-ins start from `scale: 0.001`, never `0`.

## Motion
| Helper | Use |
|---|---|
| `push(tl, cam, i, from, to, ox, oy)` | Slow camera push across scene i. Every scene gets one. |
| `shake(tl, el, t, dur, amp)` | Camera shake (countdowns, landings, OUCH!). |
| `wobble(tl, el, t0, t1, amp, period, prop)` | Ambient loop: tails, flowers, bobbing boats, floating stars. |
| `flicker(tl, flame, t0, t1)` | Flame, candle, lamp flicker. |
| `words(host, SPANS[i], opts)` + `popWords(tl, spans, big)` | The story words pop in on the exact narration times. `opts`: `top`, `left`, `size`, `italic`, `light`, `color: {wordIndex: col}`, `map: {wordIndex: "text"}`. |
| Scallop wipes (the `#fx` block) | Paper panels that slide across at chosen cuts: `plan = [[sceneIndex, colour], …]`. |

## A new scene, in order
1. `const { host, cam } = scene("s5"); const T = START[4];`
2. Background: `bgRect` + hills/sea/room shapes.
3. Characters and props (`make<Name>(cam, …)`).
4. Entrances at `T + 0.05 …`, the main action on the word it belongs to (`W[index].t`), ambient `wobble`s until `END[4]`.
5. `push(tl, cam, 4, 1.0, 1.06)` and `popWords(tl, words(host, SPANS[4], {top: 70}))`.

## The ending
`s15` (a paper card on threads) and `s16` (felt letters dropping on threads) are the Paper Rocket's own ending. Replace their text with your own ending ("The End", "Goodnight, little one", your channel name).

## Common mistakes
- Words covering a character: move `top`, or put the words on a cream paper strip.
- A scene with nothing moving after its entrance: add a `wobble` or a slow drift.
- Felt filters are heavy. Keep each scene under ~150 felt shapes; draw star fields with plain `E("circle")`.
