import json, sys
from pathlib import Path
M = {"01": "Mapas geopolítica", "02": "Documentário de negócios", "03": "Finanças com stock footage", "04": "Canal de história simples",
     "05": "Iceberg", "06": "Bonecos 2D", "07": "Metáfora com personagem fixo", "08": "Psicologia sombria", "09": "Comparação de tamanho 3D",
     "10": "Ciência em motion 2D", "11": "Mapas ilustrados", "12": "História do Reddit", "13": "3D técnico"}
base = Path(str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS"))
targets = [(d / "edit.json", M.get(d.name[:2])) for d in base.iterdir() if (d / "edit.json").exists()]
targets.append((Path(str(__import__("pathlib").Path(__file__).resolve().parents[2] / "kits" / "clay-retencao" / "edit.json")), "Clay 3D (reels)"))
for f, est in targets:
    if not est:
        continue
    j = json.loads(f.read_text(encoding="utf-8"))
    j["estilo"] = est
    f.write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f.parent.name, "->", est)
