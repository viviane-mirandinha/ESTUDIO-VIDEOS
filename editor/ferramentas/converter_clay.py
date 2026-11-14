"""Converte kits/clay-retencao (template.html + build.py) para edit.json + template local."""
import json, re, shutil, sys
from pathlib import Path
P = Path(sys.argv[1] if len(sys.argv) > 1 else str(__import__("pathlib").Path(__file__).resolve().parents[2] / "kits" / "clay-retencao"))
orig = P / "template_original.html"
if not orig.exists():
    shutil.copy2(P / "template.html", orig)
src = orig.read_text(encoding="utf-8")
(P / "fonts").mkdir(exist_ok=True)
if not (P / "fonts/Inter.ttf").exists():
    shutil.copy2(P / "hf/fonts/Inter.ttf", P / "fonts/Inter.ttf")

# palavras (mesma limpeza do build.py original)
w = json.loads((P / "words.json").read_text(encoding="utf-8"))
words, i = [], 0
while i < len(w):
    x = w[i]
    if x["w"].lower() == "dar" and i + 1 < len(w) and w[i + 1]["w"].lower().startswith("que"):
        words.append({"w": "dark" + w[i + 1]["w"][3:], "s": x["s"], "e": w[i + 1]["e"]}); i += 2; continue
    if x["w"].lower() == "a" and i + 1 < len(w) and w[i + 1]["w"].lower().startswith("reten") and x["s"] > 36:
        i += 1; continue
    if x["w"].lower().startswith("reten") and x["s"] > 36:
        x = dict(x, w="RETENÇÃO")
    words.append(x); i += 1

DUR = 42.5
items = []
def add(**k):
    k.setdefault("by", "template"); items.append(k)
TAGS = [[0, "O MITO"], [7.6, "O ALGORITMO"], [14.1, "RETENÇÃO"], [27.6, "CORRIGIR"], [34.9, "O QUE CONTA"]]
for n, (s, t) in enumerate(TAGS):
    e = TAGS[n + 1][0] if n + 1 < len(TAGS) else DUR
    add(id=f"tag{n}", type="text", track="topo", label=f"Capítulo: {t}", start=s, dur=round(e - s, 2), props={"text": t})
CH = re.search(r"const CHIPS=\[(.*?)\]\];", src, re.S).group(1)
for n, m in enumerate(re.finditer(r'\[([\d.]+),([\d.]+),"([^"]*)","([^"]*)","([^"]*)",(\d)\]', CH)):
    a, b, ic, l, v, hot = m.groups()
    add(id=f"chip{n}", type="text", track="topo", label=f"Selo: {l}", start=float(a), dur=round(float(b) - float(a), 2),
        props={"text": l, "sub": v, "icone": ic, "laranja": hot == "1"})
SRC = [[10.4, 27.55, "Ajuda do YouTube", "· como o YouTube recomenda vídeos"], [27.65, 34.75, "YouTube Studio", "· relatório de retenção de público"]]
for n, (a, b, nm, d) in enumerate(SRC):
    add(id=f"fonte{n}", type="text", track="topo", label=f"Fonte: {nm}", start=a, dur=round(b - a, 2), props={"text": nm, "sub": d})
STX = {"st0": "MITO", "st1": "SEGURA GENTE", "st2": "TEMPO > VOLUME"}
for sid, a, b in [["st0", 1.45, 3.1], ["st1", 24.45, 26.2], ["st2", 35.0, 36.6]]:
    add(id=sid, type="text", track="carimbos", label=f"Carimbo: {STX[sid]}", start=a, dur=round(b - a, 2), props={"text": STX[sid]})
LB = re.search(r"const LABELS=\[(.*?)\];", src, re.S).group(1)
for n, m in enumerate(re.finditer(r'txt:"([^"]*)",a:([\d.]+),b:([\d.]+)', LB)):
    t, a, b = m.groups()
    add(id=f"lab{n}", type="text", track="setas", label=f"Seta: {t}", start=float(a), dur=round(float(b) - float(a), 2), props={"text": t})
add(id="legenda", type="caption", track="legenda", label="Legenda", start=0, dur=DUR, props={"words": words, "keywords": ["RETEN"]})
add(id="cta", type="text", track="cta", label="Final: chamada", start=36.55, dur=round(DUR - 36.55, 2),
    props={"text": "Você olha isso no seu canal?", "palavra": "RETENÇÃO", "comenta": "Comenta", "rodape_forte": "Siga o SEU CANAL",
           "rodape": "pra mais\nestratégia de canal dark."})
items.append({"id": "marca", "type": "param", "label": "Marca (canto superior)", "props": {"value": "SEU CANAL · CANAL DARK"}})

W_ = "sfx/whoosh.wav"
edit = {"version": 1, "name": "Clay 3D — Retenção (canal dark)", "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#141518"},
        "duration": DUR, "template": "local", "fonts": {"InterL": "fonts/Inter.ttf"},
        "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
                  "extra": [{"id": f"w{k}", "src": W_, "start": s, "volume": 0.18, "label": "whoosh"} for k, s in enumerate([7.45, 14.0, 27.45, 36.35])]},
        "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "topo", "name": "Capítulo / selos"}, {"id": "setas", "name": "Setas 3D"},
                   {"id": "carimbos", "name": "Carimbos"}, {"id": "legenda", "name": "Legenda"}, {"id": "cta", "name": "Final"},
                   {"id": "textos", "name": "Textos extras"}],
        "items": items}


def R(old, new):
    global src
    assert old in src, old
    src = src.replace(old, new, 1)


R("const WORDS=__WORDS__;", "const EDIT=__EDIT__; const ED=Object.fromEntries(EDIT.items.map(i=>[i.id,i]));\n"
  "const VIS=id=>ED[id]&&!ED[id].hidden; const T0=id=>ED[id].start, T1=id=>ED[id].start+ED[id].dur;\n"
  "const WORDS=VIS('legenda')?ED.legenda.props.words:[];")
src = re.sub(r"const TAGS=\[\[.*?\]\];", lambda m: "const TAGS=EDIT.items.filter(i=>/^tag\\d/.test(i.id)&&!i.hidden).map(i=>[i.start,i.props.text]); if(!TAGS.length)TAGS.push([0,'']);", src)
src = re.sub(r"const CHIPS=\[.*?\]\];", lambda m: "const CHIPS=EDIT.items.filter(i=>/^chip\\d/.test(i.id)&&!i.hidden).map(i=>[i.start,i.start+i.dur,i.props.icone,i.props.text,i.props.sub,i.props.laranja?1:0]);", src, flags=re.S)
src = re.sub(r"const SRC=\[\[.*?\]\];", lambda m: "const SRC=EDIT.items.filter(i=>/^fonte\\d/.test(i.id)&&!i.hidden).map(i=>[i.start,i.start+i.dur,i.props.text,i.props.sub]);", src)
src = re.sub(r"const STAMPS=\[.*?\];", lambda m: "const STAMPS=['st0','st1','st2'].filter(VIS).map(id=>{document.getElementById(id).textContent=ED[id].props.text;return [id,T0(id),T1(id)];});", src)
cnt = [0]
def lab(m):
    k = cnt[0]; cnt[0] += 1
    return f"txt:ED.lab{k}.props.text,hid:!!ED.lab{k}.hidden,a:T0('lab{k}'),b:T1('lab{k}')"
R(LB, re.sub(r'txt:"[^"]*",a:[\d.]+,b:[\d.]+', lab, LB))
R("const op=win(t,L.a,L.b,0.25);", "const op=L.hid?0:win(t,L.a,L.b,0.25);")
R("const ck=sm((t-36.55)/0.5);", "const CS=VIS('cta')?T0('cta'):1e9; const ck=sm((t-CS)/0.5);")
R("const pressT=[38.7,39.3,39.9,40.5];", "const pressT=[2.15,2.75,3.35,3.95].map(x=>CS+x);")
R("(t-(37.15+i*0.16))", "(t-(CS+0.6+i*0.16))")
R("t>36.55&&false", "false")
R('SEU CANAL · CANAL DARK</div>', '<span id="marcaTxt"></span></div>')
R('<div class="t">Você olha isso no seu canal?</div>', '<div class="t" id="ctaT"></div>')
R('<div class="c">Comenta <b>RETENÇÃO</b></div>', '<div class="c"><span id="ctaC"></span> <b id="ctaW"></b></div>')
R('<div class="f"><b>Siga o SEU CANAL</b> pra mais<br>estratégia de canal dark.</div>', '<div class="f"><b id="ctaF1"></b> <span id="ctaF2"></span></div>')
R(' <div id="cap"></div>\n</div>', ' <div id="cap"></div>\n <!--__ITEMS__-->\n</div>')
R("renderAt(window.__hfThreeTime||0);", """{const c=ED.cta.props; $("ctaT").textContent=c.text; $("ctaC").textContent=c.comenta; $("ctaW").textContent=c.palavra;
 $("ctaF1").textContent=c.rodape_forte; $("ctaF2").innerHTML=String(c.rodape||"").replace(/[<>&]/g,"").replace(/\\n/g,"<br>");
 $("marcaTxt").textContent=(ED.marca&&ED.marca.props.value)||"";}
renderAt(window.__hfThreeTime||0);""")
(P / "template.html").write_text(src, encoding="utf-8")
(P / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", len(items), "itens")
