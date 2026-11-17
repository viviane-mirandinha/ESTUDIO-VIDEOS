# embutir.py — monta <pasta>/template.html = modelo.html + motor.js + cenarios.js + <pasta>/cenas.js + fontes.
# Uso:  python kits/animacao-2d/embutir.py <pasta-do-video>      (pode repetir à vontade)
import sys, base64, pathlib
K = pathlib.Path(__file__).parent; R = K.parent.parent
pasta = pathlib.Path(sys.argv[1]).resolve()
b64 = lambda p: base64.b64encode((R / "recursos" / "fontes" / p).read_bytes()).decode()
ler = lambda p: p.read_text(encoding="utf-8")
cenas = pasta / "cenas.js"
if not cenas.exists(): cenas = pasta.parent / "cenas.js"      # capítulo: usa as cenas do projeto (pasta-mãe)
if not cenas.exists(): sys.exit(f"ERRO: falta cenas.js em {pasta} ou na pasta-mãe")
t = ler(K / "modelo.html")
t = t.replace("/*__MOTOR__*/", ler(K / "motor.js")).replace("/*__CENARIOS__*/", ler(K / "cenarios.js")).replace("/*__CENAS__*/", ler(cenas))
t = t.replace("__F_CINZEL__", b64("Cinzel-700.woff")).replace("__F_CAVEAT__", b64("Caveat-700.ttf"))
import re, mimetypes
def _img(m):
    nome = m.group(1)
    for base in (pasta / "img", pasta.parent / "img"):
        p = base / nome
        if p.exists():
            return "data:" + (mimetypes.guess_type(p.name)[0] or "image/jpeg") + ";base64," + base64.b64encode(p.read_bytes()).decode()
    sys.exit(f"ERRO: imagem {nome} não encontrada em img/")
t = re.sub(r"__IMG\(([^)]+)\)__", _img, t)
import json
try: _cv = json.loads((pasta / "edit.json").read_text(encoding="utf-8")).get("canvas", {})
except Exception: _cv = {}
if (_cv.get("h") or 0) > (_cv.get("w") or 0):      # formato em pé (9:16): palco 16:9 no meio + título em cima + legenda embaixo (vertical.css/js)
    t = t.replace("</style></head>", ler(K / "vertical.css") + "</style></head>", 1).replace("<!--__ITEMS_SCRIPT__-->", "<script>" + ler(K / "vertical.js") + "</script><!--__ITEMS_SCRIPT__-->", 1)
(pasta / "template.html").write_text(t, encoding="utf-8")
print("template.html montado:", len(t) // 1024, "KB")
