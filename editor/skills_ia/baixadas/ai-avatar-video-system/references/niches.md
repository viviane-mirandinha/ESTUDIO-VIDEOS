# Niche Adaptation — reference

This skill is niche-agnostic. Nothing in it is specific to food or health. What it locks — face, environment, voice, speech-while-acting — is identical for a mechanic, a gardener, a barber or a financial advisor.

Only four variables change per niche. Fill them once, at the start of the project, and every rule above applies unchanged.

### The four niche variables

| Variable | What it is | Why it matters |
|---|---|---|
| **ACTION PLATE** | The surface or object the hands work on | Replaces "work surface" everywhere. It is where the hands live |
| **STATIONS** | The distinct positions the character works from | Each station needs its own Master Scene (VR-A15) |
| **DIEGETIC AUDIO** | The real sounds the action makes | Goes in the AUDIO block of every video prompt. Without it the model adds music |
| **PROOF OBJECTS** | The props that make the character credible before he speaks | Populate the Master Scene. They are the visual argument |

### Filled examples

| Niche | Action plate | Stations | Diegetic audio | Proof objects |
|---|---|---|---|---|
| **Mecânico** | Engine bay, workbench, wheel | Hood open · under the raised car · bench with the part in hand | Ratchet clicks, metal on metal, bolt loosening, hood creak | Worn tool chest, oil-stained rag, torque wrench, parts in labeled bins, grease on the hands |
| **Cozinha / receita** | Countertop, stove | Counter · stove · plating | Chopping, sizzling, pouring, pot lid | Cast iron, jars, aged wooden board |
| **Jardim / plantas** | Potting bench, soil bed | Bench · ground level · greenhouse shelf | Soil crumbling, water, snips cutting, pot scrape | Clay pots, hand tools, dirt under the nails |
| **Marcenaria / DIY** | Workbench, the piece itself | Bench · saw station · assembly floor | Sanding, plane shaving, hammer, drill | Sawdust, clamps, pencil behind the ear, worn bench top |
| **Barbearia / estética** | Barber chair, counter | Chair · back counter | Scissors, clipper hum, spray, water | Old chair, mirror, bottles, towels |
| **Finanças / negócio** | Desk, notebook | Desk · whiteboard | Pen on paper, page turn, chair creak | Handwritten ledger, printed statements, calculator, framed certificates |
| **Pet** | Grooming table, floor | Table · floor with the animal | Clipper, brush, animal sounds | Leashes, brushes, worn table surface |
| **Construção / reforma** | Wall, floor, the fixture | The wall · the floor · the tool table | Drill, trowel, tile snap, level tap | Dust, level, chalk lines, scuffed knee pads |

### How to fill them for a new niche

Ask the user, or infer from the Master Scene image:

1. **"Onde as mãos dele trabalham?"** → action plate
2. **"Ele trabalha de quantas posições diferentes?"** → stations (one Master Scene each)
3. **"Que barulho essa ação faz de verdade?"** → diegetic audio
4. **"O que tem nesse lugar que prova que ele faz isso há 30 anos?"** → proof objects

### Niche-specific cautions

**Hands-dirty niches (mechanic, garden, construction).** The dirt is continuity. If the hands are greasy in scene 03 they stay greasy in scene 04. State it in the ALREADY PRESENT block or the model cleans them between scenes.

**Tool-heavy niches.** Tools are objects with state. A wrench set down in scene 02 is still on the bench in scene 03. Same tracking as ingredients.

**Desk / talking-head niches (finance, law, coaching).** The weakest for this format, because the physical action is thin. Give the character something real to do with the hands — writing a figure, turning a page, sliding a document across the desk. A pure talking head with idle hands is exactly where the model drifts.

**Animal or people-facing niches (pet grooming, barber).** A second living subject in frame multiplies the drift. Keep the second subject out of the identity references, describe it in plain terms in each prompt, and accept that it will not be consistent across scenes. Frame it so this does not matter — hands and back of the head, not its face.

**VR-A22 — The four niche variables are defined before Scene 01 and written into the project header.** They are referenced by every prompt. Changing the action plate mid-project has the same effect as changing the Master Scene: the project restarts.

---

