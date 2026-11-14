---
name: ai-avatar-video-system
description: Produces complete scene plans, image prompts and Gemini Omni Flash video prompts for short vertical videos starring a recurring AI avatar who speaks to camera while performing an action. Locks face identity, environment and voice across every scene, in any language and any niche. Use this skill ANY time the user is working on AI avatar videos, AI characters, faceless video pages, talking-head AI content, Omni Flash, Google Flow, or asks for scene prompts, first-frame prompts, image-to-video prompts, character consistency, scenario consistency or voice consistency — even if they only mention a character, a script, a scenario image or reference screenshots without naming the workflow.
---

# AI Avatar Video System — Skill v1.0

Target model: **Gemini Omni Flash** (`gemini-omni-1.1-flash`), via Google Flow or the Gemini app.
Scope: short vertical videos where a **recurring AI character speaks to camera WHILE performing an action**, in a recurring environment.

This skill is separate from the Recipe Production System. Do not mix rules between them.

---

## 1. Purpose

Produce, for a single recurring character:

1. a **scene plan** (how many scenes, what happens in each);
2. **image prompts** for every first frame;
3. **Omni Flash video prompts** that animate those frames with synchronized speech + action;
4. **identity, environment and voice continuity** across every scene and every language.

The character must be recognizable as the same person in scene 01 and scene 12. The environment must be the same room. The voice must sound like the same throat.

---

## 2. What Omni Flash actually does — hard facts

These are model constraints, not preferences. Every rule downstream exists because of them.

| Fact | Consequence for this skill |
|---|---|
| Generates **native audio with the video**, including speech | Dialogue is written inside the video prompt, not added later |
| **Defaults to multiple shots** and invents a narrative | Every prompt MUST force a single continuous shot, or the face changes mid-clip |
| **Voice editing is not supported** | Voice cannot be corrected after the fact. It must be right on generation |
| **Audio reference upload is not supported** | Voice cannot be cloned. Consistency comes ONLY from a fixed textual voice description + multi-turn |
| **English is the only fully evaluated language** | Other languages work but vary. Requires the language protocol in §9 |
| Negative prompt parameter does not exist | All negatives go inside the prompt body as plain sentences |
| Supports `<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_N>`, `<VIDEO_REF_N>` and `[# Sources] [# References]` | This is the identity-lock mechanism. Always use it |
| Video references: max 3 clips, 3s each; their audio is ignored | A video reference locks likeness, never voice |
| Extension: 10s at a time, up to 40s total | Long single takes are built by extension, not by stitching separate generations |
| Dialogue CAN be added when extending a video the model generated (multi-turn) | Best voice continuity path |
| Dialogue CANNOT be added when extending an UPLOADED video | Never plan a talking extension from an uploaded clip |
| Timecode syntax `[0-3s]` is understood | Use it to synchronize speech with action |
| Supports 9:16 | Always specify vertical |

---

## 3. Accepted inputs

The user may provide any combination of:

- **Character Sheet** — the front+profile identity image of the avatar;
- **Master Scene** — the empty environment image;
- **Reference frames** — screenshots taken from a competitor/reference video;
- **Script** — the narration the character will speak;
- **Idea only** — a topic with no script.

The user cannot provide video files for analysis. If the user mentions a reference video, respond once:

**"Não consigo assistir vídeo. Me manda prints dos momentos que importam — cada troca de ação ou de objeto — que eu monto as cenas a partir deles."**

Then proceed with whatever prints arrive.

---

## 4. Mandatory questions before planning

Ask only what is genuinely missing. Never ask twice.

1. **"Qual a duração final do vídeo?"** (ex.: 20s, 30s, 45s, 60s)
2. **"Em qual idioma o personagem fala?"** (pt-BR, en-US, es-LATAM…)
3. If no Character Sheet was supplied: **"Me manda a ficha de identidade do personagem."**
4. If no Master Scene was supplied: **"Me manda a imagem do cenário."**

Do not begin scene planning while 1 and 2 are unknown. Items 3 and 4 may be produced on the fly if the user asks, but must exist before any prompt is written.

---

## 5. The three locks

Every production runs on three fixed assets. They are created ONCE and never renegotiated mid-project.

### LOCK 1 — Character Sheet
The front+profile identity image. Authority over: face, bone structure, skin, hair, facial hair, signature accessory, wardrobe.
It is NEVER the authority over: environment, camera, action, props.

### LOCK 2 — Master Scene
The empty environment image. Authority over: room, walls, work surface, lighting direction and color, camera height, permanent props.
It is NEVER the authority over: the character, or any object that moves.

### LOCK 3 — Voice Profile
A fixed block of text, written once, pasted **verbatim, word for word, in every single video prompt of the project**. See §8.

**VR-A01 — The three locks are written before Scene 01 and never edited mid-project.**
If any lock changes, the project restarts. A "small tweak" to the voice line in scene 07 produces a different person's voice.

---

## 6. Entry modes

### MODE A — Reference frames supplied

1. Read every print before writing anything. Never plan from print 01 alone.
2. Build the **action inventory**: for each print, record what the hands are doing, what object is in play, what has already been used, what is new.
3. Collapse the inventory into **unique actions**. Repeated frames of the same continuous action are ONE scene, not three.
4. A new scene is created only when one of these changes:
   - the object in the hands;
   - the physical action;
   - the state of the material being worked on;
   - the station/location.
5. Camera moves, zoom-ins and framing changes in the reference are NOT scenes. Ignore them.
6. Never invent an intermediate step that is not visible in the prints.

### MODE B — Script supplied, no reference

1. Split the script into **speech beats** — one complete idea per beat.
2. Assign each beat a **physical action** that a person would plausibly be doing while saying it. Never leave a beat with the character just talking.
3. Merge beats that share the same action into one scene.
4. Split any beat whose spoken length exceeds the clip budget (§7).

### MODE C — Idea only, no script

1. Write the script first, in the user's chosen language, at the target duration.
2. Present the script for approval BEFORE writing any prompt.
3. Then run Mode B.

---

## 7. Duration and speech budget

This is the single most common failure. A prompt that asks for 30 words in an 8-second clip produces rushed, robotic, clipped speech.

**Speech rate, spoken naturally:**

| Language | Words per second | Words in 8s |
|---|---|---|
| pt-BR | ~2.4 | 17–19 |
| en-US | ~2.6 | 19–21 |
| es-LATAM | ~2.5 | 18–20 |

Rules:

- Reserve ~1s at the start (character settles, breath) and ~0.5s at the end.
- **Usable speech window in an 8s clip is ~6.5s.**
- If a beat exceeds the window, split the scene. Never speed up the delivery.
- Silent action scenes are allowed and encouraged — they let the edit breathe and they are far more reliable to generate.

**VR-A02 — Word count is validated before the prompt is written, not after the clip comes back wrong.**

---

## 7b. Generation duration — MANDATORY on every video prompt

Every video prompt must state the duration to select in the generator. The user should never have to guess.

### Available durations

Flow exposes discrete options — currently **4s, 6s and 8s** per generation. Extension adds up to a **40s total**. Confirm the options in the interface before committing, since the UI changes.

Never write a duration that is not selectable. "7 seconds" is not an option and forces the user to round it themselves.

### How to choose

| Scene type | Duration | Why |
|---|---|---|
| Silent quick action (place, pick up, point at, attach) | **4s** | The action completes fast. Longer = the model invents extra motion |
| Silent action with material or mechanical response (pour, stir, loosen, unscrew, sand, fold) | **6s** | Needs time for the physics to read |
| Talking, short beat (up to 10 words) | **6s** | ~4.5s usable speech window |
| Talking, full beat (11–19 words) | **8s** | ~6.5s usable speech window. Default for talking scenes |
| Hook / opening line | **8s** | Needs the settle, the eye contact and the full line |
| Final result / reveal | **6s** | Long enough to land, short enough not to drift |

### Rules

**VR-A18 — Never exceed 8s in a single generation.** Past 8s Omni Flash starts inventing camera moves and shot cuts, and the face drifts. A longer beat is built by extension, never by a longer single generation.

**VR-A19 — Talking scenes default to 8s.** Only drop to 6s when the line is 10 words or fewer.

**VR-A20 — A silent action scene never gets 8s.** Extra seconds with nothing to do produce invented motion, a second action, or an unprompted camera move.

**VR-A21 — Match the duration to the word count, not the other way around.** If the line needs more than 8s, split the scene. Do not compress the delivery.

The duration goes in two places, always:
1. As a labeled line above the prompt block, for the user to set in the interface;
2. Inside the prompt body, as the closing timing instruction.

---

## 8. The Voice Profile — the core of this skill

Because voice cannot be cloned or edited, the ONLY consistency mechanism is a rigid textual description repeated identically.

### Structure

Write it once, with all seven fields filled:

```
VOICE: [age] year old [gender], [origin/accent]. [Timbre]. [Pace].
[Pitch and volume]. [Speech habit]. Speaking [language] natively with a
[regional] accent. Warm, unhurried, talking to one person, not performing
to an audience. Natural breaths between sentences. Slight imperfections in
delivery. Not an announcer, not a narrator, not a voiceover.
```

### Filled example

```
VOICE: 74 year old man, rural Brazilian. Low, slightly gravelly, dry throat.
Slow and deliberate, pausing between thoughts. Medium-low pitch, quiet volume
as if the listener is close. Ends sentences by trailing off slightly rather
than punching the last word. Speaking Brazilian Portuguese natively with an
interior São Paulo accent. Warm, unhurried, talking to one person, not
performing to an audience. Natural breaths between sentences. Slight
imperfections in delivery. Not an announcer, not a narrator, not a voiceover.
```

### Why each field matters

- **Age + gender + origin** — sets the fundamental timbre. Without it the model defaults to a neutral 35-year-old broadcaster.
- **Timbre** — the texture. "Gravelly", "breathy", "clear", "nasal", "raspy".
- **Pace** — the biggest driver of the robotic effect. Slow and deliberate reads as human; fast and even reads as TTS.
- **Pitch and volume** — "quiet, as if the listener is close" is the single most effective anti-robot instruction. It forces conversational delivery.
- **Speech habit** — one idiosyncrasy. Trailing off, a small laugh, clearing the throat. This is the fingerprint.
- **Language + accent** — see §9.
- **The closing negatives** — "not an announcer, not a narrator, not a voiceover" blocks the default TTS register.

### Rules

**VR-A03 — The Voice Profile is pasted verbatim in every video prompt. Not summarized, not shortened, not paraphrased.** A single reworded adjective changes the voice.

**VR-A04 — Never write "the same voice as before".** The model has no memory between separate generations. The description IS the memory.

**VR-A05 — Prefer multi-turn extension when a beat needs more than one clip.** Extending a model-generated video via `previous_interaction_id` carries the voice forward far more reliably than a fresh generation. Uploaded videos cannot receive new dialogue.

---

## 9. Multilingual protocol

The model is only fully evaluated in English. Other languages work but drift. These rules contain the drift.

1. **The prompt body stays in English. The dialogue line stays in the target language.** Never translate the prompt into Portuguese to "help" — it degrades everything except the dialogue.

2. **Name the language AND the region, always:**
   - `Speaking Brazilian Portuguese with a São Paulo interior accent` — good
   - `Speaking Portuguese` — bad, may produce European Portuguese
   - `Speaking Latin American Spanish with a Mexican accent` — good
   - `Speaking Spanish` — bad, may produce Castilian with a lisp

3. **Add the accent-lock sentence for any non-English language:**
   ```
   No English accent, no foreign accent, no translated-sounding phrasing.
   Native speaker rhythm and natural regional intonation.
   ```

4. **Write dialogue the way it is spoken, not the way it is written.** Contractions, dropped syllables, informal register. `"cê tá vendo isso aqui?"` produces natural speech; `"você está vendo isso aqui?"` produces reading.

5. **A new language = a new Voice Profile and a new project.** The same character speaking Portuguese and Spanish will not have the same voice. Treat each language as a separate production line with its own locked profile. Never promise cross-language voice identity.

6. Numbers, units and brand names in the dialogue must be spelled phonetically in the target language: `"duzentos e cinquenta gramas"`, not `"250g"`.

---

## 10. Image prompt rules — the first frame

The still is the EXACT first frame of the video. It must be built so speech and action can begin naturally from it.

**VR-A06 — In a talking scene the first frame has the mouth CLOSED or barely parted, and the eyes ON the lens.** A first frame with the mouth wide open forces the model to start mid-syllable and the audio stutters.

**VR-A07 — The hands are already in position, at the start of the action, not mid-action.** Hands resting on the object, not halfway through the movement.

**VR-A08 — The head is UP, chin level, looking at camera, even when the hands are busy at the action plate.** Explicitly state it or the model will point the face downward at the hands.

**VR-A09 — If the character wears a hat, add `hat brim tilted slightly back so both eyes are fully lit and clearly visible`.** Otherwise the brim shadows the eyes and the clip reads as dead.

### Image prompt template

```
[# Sources <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2]

Use <IMAGE_REF_0> as the exact identity of the person: face, bone structure,
skin texture, hair, facial hair and signature accessory. Do not alter the face.

Use <IMAGE_REF_1> as the exact environment: room, work surface, walls,
permanent props, lighting direction, color temperature and camera height.
Do not redesign the environment.

[If continuing from a previous scene:]
Use <IMAGE_REF_2> only for the accumulated state of the work surface.
It has no authority over identity or environment.

The previous action is COMPLETELY FINISHED. There is no [previous object /
previous motion] in frame.

CREATE THIS FRAME:
[ONE action, at its beginning, in concrete physical terms.]

The character's hands are at the ACTION PLATE, already in position on
[object], at the very start of the movement. His head is UP, chin level,
looking DIRECTLY INTO THE CAMERA LENS. Mouth closed or barely parted.
Both eyes fully visible and lit, small natural catchlights.

ALREADY PRESENT: [objects that must persist, with their state]
MUST NOT APPEAR: [objects from other scenes, next-step objects, duplicates]

Integration: the light on the character matches the environment exactly in
direction, softness and color. Contact shadows under the forearms and under
every object. Same depth of field as the environment — the character is not
sharper than the background.

Vertical 9:16. Ultra photorealistic. Shot on a phone camera. Visible skin
texture and pores. Not glamorous, not a stock photo, no text, no watermark.
```

---

## 11. Omni Flash video prompt template

Every video prompt is complete and standalone. The user never concatenates a base prompt.

Above every video prompt, print this line so the user knows what to set in the interface:

```
⏱ GERAR COM: 8s · 9:16 · Modelo: Gemini Omni Flash
```

Then the prompt:

```
[# Sources <FIRST_FRAME>@Image1]

Use Image1 as the exact first frame.

SINGLE CONTINUOUS SHOT. No scene cuts. No second shot. No camera cut.
The camera is locked: no zoom, no pan, no tilt, no dolly, no shake.
Preserve the environment, props, lighting, framing and the person's face
and clothing exactly as they appear in the first frame. Do not restyle.

ACTION:
[0-Xs] [The physical action, continuing from the position in the first frame.
Describe hands, object, material response. It completes naturally within the
clip.]

The character performs this action WHILE speaking. He does not stop working
to talk, and he does not stop talking to work. His eyes stay on the camera
for most of the clip, glancing down at his hands only briefly.

DIALOGUE — he says exactly this, once, and nothing else:
"[the line, in the target language, written as spoken]"

[VOICE PROFILE — pasted verbatim, all seven fields]

No English accent, no foreign accent, no translated-sounding phrasing.
Native speaker rhythm and natural regional intonation.

AUDIO: only his voice and the natural sounds of the action
([specific diegetic sounds]). No background music. No added sound effects.
No second voice. No narrator.

Do not add any words beyond the dialogue above. Do not repeat the line.
Do not add on-screen text, captions or subtitles. No watermark.

Natural human motion. Realistic physics. Ultra photorealistic.
Vertical 9:16.

The action and the dialogue both complete naturally within X seconds.
Do not extend beyond the action. Do not add a second beat to fill time.
```

### For a silent action scene

Replace the dialogue and voice blocks with:

```
No dialogue. No speech. No narration. No music.
AUDIO: only the natural sounds of the action ([specific sounds]).
```

### For an extension (beat longer than one clip)

```
[# Sources <PREVIOUS_VIDEO>@Video1]

Extend this video. The scene continues, same shot, same camera, same person,
same environment, same voice.

[0-Xs] [continuation of the action]

He continues speaking in the same voice and says exactly this:
"[next line]"

[VOICE PROFILE — pasted verbatim again]

Same audio treatment. No music. No scene cut. No new character.
```

---

## 12. Continuity rules

**VR-A10 — One action per scene.** Two actions in one clip produces a scene cut, and a scene cut produces a new face.

**VR-A11 — Cancel the previous action explicitly.** Every image prompt states what is FINISHED and what is NOT in frame. Without this the model carries the previous object into the new scene.

**VR-A12 — Track the state of the action plate across scenes.** What was added stays added. What was removed stays removed. What was opened stays open. Write the accumulated state into every prompt's ALREADY PRESENT block.

**VR-A13 — Use the minimum number of references.** Character Sheet + Master Scene is the default. Add the previous scene ONLY when the accumulated state is too complex to describe in words. Every extra reference is another chance for the model to average faces.

**VR-A14 — The previous scene is continuity, never identity.** State this in the prompt every time it is used.

**VR-A15 — Station change resets the environment authority.** If the character moves to a different surface, angle or area, a new Master Scene is required. Never improvise a second environment from the first. A mechanic moving from the open hood to under the raised car is a station change. A cook moving from the counter to the stove is a station change. The same room does not mean the same station.

**VR-A16 — Never let the model choose the framing.** State the shot size explicitly in every scene: medium shot, medium close-up, close-up on hands. Variation across scenes is good for the edit but must be deliberate, and any close-up on hands must still be generated from the same Master Scene.

**VR-A17 — Eye contact must be restated in every talking prompt.** The model drifts toward downward gaze on every action-based clip.

---

## 13. Output format

Deliver in this exact structure. Labels in Brazilian Portuguese, prompts in English, dialogue in the target language.

```
## PLANO DE CENAS

Duração alvo: Xs · Idioma: [idioma] · Total de cenas: N

| Cena | Ação | Fala | Palavras | Gerar com |
|------|------|------|----------|-----------|
| 01   | ...  | ...  | 18       | 8s        |
| 02   | ...  | (muda) | —      | 4s        |

**Soma das gerações:** Xs
```

Then, per scene:

```
## CENA 01 — [NOME DA AÇÃO]

**O que acontece:** [uma frase]
**Enviar como referência:**
- Imagem 1: Ficha do personagem
- Imagem 2: Cenário master
- Imagem 3: [apenas se necessário]

### IMAGEM
```text
[prompt de imagem completo]
```

### VÍDEO — Omni Flash
**Primeiro frame:** imagem gerada da CENA 01

⏱ **GERAR COM: 8s · 9:16 · Gemini Omni Flash**

```text
[prompt de vídeo completo, com o Voice Profile colado por inteiro]
```
```

Repeat for every scene. Never require assembly.

---

## 14. Pre-delivery validation

Before delivering the batch, verify every scene:

**Identity and environment**
- [ ] Character Sheet referenced in every image prompt
- [ ] Master Scene referenced in every image prompt
- [ ] Previous-scene reference used only where justified, and labeled as continuity only

**First frame**
- [ ] Mouth closed or barely parted
- [ ] Eyes on lens, chin level
- [ ] Hands in position at the START of the action
- [ ] Hat brim clause present if the character wears a hat
- [ ] Integration block present (light match, contact shadows, matched depth of field)

**Video prompt**
- [ ] "SINGLE CONTINUOUS SHOT. No scene cuts." present
- [ ] Camera lock present
- [ ] Voice Profile pasted VERBATIM, all seven fields, identical to every other scene
- [ ] Accent-lock sentence present for non-English
- [ ] Dialogue word count inside the budget for the clip length
- [ ] "Do not add any words beyond the dialogue above" present
- [ ] Music and extra SFX explicitly excluded
- [ ] Action and speech stated as simultaneous
- [ ] 9:16 stated

**Duração**
- [ ] The ⏱ GERAR COM line is printed above every video prompt
- [ ] The duration is a selectable option (4s, 6s or 8s) — never 5s, 7s or 10s
- [ ] No single generation exceeds 8s
- [ ] Talking scenes at 8s unless the line is 10 words or fewer
- [ ] Silent action scenes at 4s or 6s, never 8s
- [ ] The same number appears in the ⏱ line and in the prompt body

**Sequence**
- [ ] One action per scene
- [ ] Previous action explicitly cancelled
- [ ] Accumulated state consistent scene to scene
- [ ] Total duration of all clips ≈ target runtime

---

## 15. Failure playbook

| Symptom | Fix |
|---|---|
| Face changes mid-clip | The shot cut. Add "SINGLE CONTINUOUS SHOT. No scene cuts. No second shot." |
| Robotic voice | Pace too fast or Voice Profile too short. Add "slow and deliberate", "quiet volume as if the listener is close", "not an announcer" |
| Speech rushed, words clipped | Word count over budget. Split the scene |
| Wrong accent | Region not named. Add country + region + accent-lock sentence |
| Character looks down the whole clip | VR-A08 and VR-A17 missing. Restate eye contact in image AND video prompt |
| Character talks but stops working | Add "he does not stop working to talk, and he does not stop talking to work" |
| Voice different from last scene | Voice Profile was paraphrased. Paste it verbatim. Consider multi-turn extension instead |
| Music appeared | "No background music. No added sound effects." missing |
| Second voice / narrator | Add "No second voice. No narrator." |
| Subject looks pasted into the room | Integration block missing from the image prompt |
| Object from scene 03 reappeared in scene 05 | MUST NOT APPEAR block missing |
| Face is an average of two people | Too many references. Drop to Character Sheet + Master Scene |
| Clip drags, character repeats the action or freezes | Duration too long for the beat. Drop from 8s to 6s or 4s |
| Model invented a camera move or a second action | Duration too long, or over 8s in one generation. Shorten and split |
| Line got cut off at the end | Duration too short for the word count. Go to 8s or split the scene |

---

## 16. Default language

Scene labels, explanations and instructions to the user: **Brazilian Portuguese**.
Generation prompts: **English**.
Dialogue inside prompts: **exactly the language the user requested**, written as spoken.

---

## 16b. Niche adaptation

This skill is niche-agnostic. Nothing in it is specific to food or health. A mechanic, a gardener, a barber, a carpenter or a financial advisor all run on the same locks.

Four variables change per niche: ACTION PLATE, STATIONS, DIEGETIC AUDIO, PROOF OBJECTS.

**Read `references/niches.md` before Scene 01 of any new project**, and any time the user names a niche that has not been produced before. It contains the definitions, eight filled niche examples, the four questions to ask the user, and the niche-specific cautions.

**VR-A22 — The four niche variables are defined before Scene 01 and written into the project header.** Changing the action plate mid-project has the same effect as changing the Master Scene: the project restarts.

---

## 17. Success definition

A successful production has:

- the same face in every scene, with no averaging or drift;
- the same room, same light, same camera height;
- one voice that sounds like one throat across the whole video;
- a character who speaks and works at the same time, looking at the viewer;
- speech that sounds like a person talking to one other person, not a voiceover;
- clip durations that sum to the target runtime;
- prompts ready to paste with zero assembly.
