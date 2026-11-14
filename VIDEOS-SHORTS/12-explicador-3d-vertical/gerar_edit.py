"""Short 12 — EXPLICADOR 3D VERTICAL. Todo tempo sai do words.json (faster-whisper) alinhado ao roteiro via at()/end().
Reaproveita _template-palco3d (palco.py + base.html) e aplica por cima o visual do estilo 12:
cabeçalho pequeno "@perfil · TEMA", rótulos em pílula com haste, legenda GRANDE branca com 1 palavra colorida."""
import os, sys, json, glob
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "_template-palco3d"))
from palco import Projeto

ROT = glob.glob(os.path.join(D, "..", "..", "ROTEIROS-SHORTS", "12 - *.txt"))[0]
NAME = "12 - 24-10-2026 - EXPLICADOR 3D VERTICAL - Como funciona um relogio de corda sem bateria"
P = Projeto(D, ROT)
at, end = P.at, P.end
DUR = round(P.voz_dur + 0.7, 2)

P.param("breadcrumb", "@explica.em3d · RELÓGIO DE CORDA", "Cabeçalho (perfil · tema)")
P.param("estrelas", 0, "Qtd. de estrelas")
P.param("fog_ini", 40, "Névoa início")
P.param("fog_fim", 95, "Névoa fim")
P.param("cor_fundo", "#0d0f15", "Cor do fundo")
P.param("cor_chao", "#171a23", "Cor do chão")
P.param("cor_destaque", "#FFD23F", "Cor da palavra destacada")

# ---- eventos 3D ----
T_COMO, T_TUDO, T_QUANDO, T_E_ALI = at("Como?"), at("Tudo começa"), at("Quando você"), at("É ali")
T_AMOLA, T_CADA, T_SOQUE, T_SE = at("A mola quer"), at("Cada engrenagem"), at("Só que"), at("Se nada")
T_QUEM, T_UMA, T_ACADA, T_ESSE = at("Quem segura"), at("Uma roda"), at("A cada"), at("Esse é o")
T_EM, T_RUB, T_COM, T_SEGUE = at("Em muitos"), at("E os rubis"), at("Com a corda"), at("Segue")
P.cena("mostrador abre", T_TUDO, T_TUDO + 1.5, id="c_abre")
P.cena("coroa gira e aperta a mola", at("gira a coroa"), end("essa mola") + 0.3, id="c_corda")
P.cena("mola brilha (energia)", T_E_ALI, T_AMOLA + 0.2, id="c_energia")
P.cena("mola solta e gira o tambor", T_AMOLA, T_SE, id="c_solta")
P.cena("fila de engrenagens acende", at("fila de engrenagens") - 0.2, T_SOQUE, id="c_fila")
P.cena("ponteiro na roda central", at("leva os ponteiros"), T_SOQUE + 0.5, id="c_ponteiros")
P.cena("sem escape: mola desenrola", T_SE, T_QUEM, id="c_problema")
P.cena("escape acende", T_QUEM, T_ACADA, id="c_escape")
P.cena("âncora acende", at("uma âncora"), at("e um volante"), id="c_ancora")
P.cena("volante acende", at("e um volante"), at("o espiral"), id="c_volante")
P.cena("espiral acende", at("molinha"), T_ACADA + 0.5, id="c_espiral")
P.cena("volante a 4 Hz (8 alternâncias/s)", at("oito vezes"), T_RUB, id="c_oito")
P.cena("rubis brilham", at("rubis"), T_COM, id="c_rubis")
P.cena("mostrador fecha", T_SEGUE - 1.0, DUR, id="c_fecha")

# ---- câmera (órbita em volta do relógio; alvo fica a ~40% da altura, acima da legenda) ----
import math
def O(cx, cy, d, az=0, el=0.08):
    ly = cy - 0.065 * d
    a, e = math.radians(az), el
    return [round(cx + d * math.sin(a) * math.cos(e), 2), round(ly + d * math.sin(e), 2), round(d * math.cos(a) * math.cos(e), 2)], [cx, round(ly, 2), 0]
BX, BY = -1.05, 3.0
P.cam("relógio inteiro", 0, *O(0, 3.3, 23, -28), trans=0)
P.cam("gira devagar", at("E mesmo"), *O(0, 3.3, 21, 12), trans=2.2)
P.cam("aproxima (abre)", T_COMO, *O(0, 3.4, 17, -6), trans=1.4)
P.cam("tambor (mola)", at("uma mola"), *O(BX, BY, 7.5, -22, .12), trans=1.2)
P.cam("coroa", T_QUANDO, *O(2.2, 3.4, 8, 38), trans=1.1)
P.cam("mola apertando", at("você aperta"), *O(BX, BY, 6, -8), trans=1.0)
P.cam("energia", T_E_ALI, *O(BX, BY, 5.2, 12, .15), trans=0.9)
P.cam("tambor + roda central", T_AMOLA, *O(-0.5, 3.2, 9, 22), trans=1.1)
P.cam("fila de engrenagens", at("fila de"), *O(0.2, 3.7, 9.5, -24), trans=1.1)
P.cam("cada vez mais rápido", T_CADA, *O(0.6, 3.9, 7.5, 24), trans=1.1)
P.cam("ponteiros", at("no caminho"), *O(0, 3.6, 9, 0, .25), trans=1.0)
P.cam("problema (afasta)", T_SOQUE, *O(0, 3.4, 15, -16), trans=1.0)
P.cam("sem freio", T_SE, *O(0, 3.4, 12, 14), trans=1.3)
P.cam("escape", T_QUEM, *O(0, 4.55, 6, -16), trans=1.0)
P.cam("roda de escape", T_UMA, *O(0.6, 4.45, 4.2, 22), trans=0.9)
P.cam("âncora", at("uma âncora"), *O(0.1, 4.75, 4.2, -12), trans=0.9)
P.cam("volante", at("e um volante"), *O(-0.95, 4.7, 4.8, -30), trans=0.9)
P.cam("espiral", at("molinha"), *O(-0.95, 4.75, 3.4, 4, .2), trans=0.9)
P.cam("ida e volta", T_ACADA, *O(-0.15, 4.6, 5.4, 16), trans=1.0)
P.cam("tic-tac", T_ESSE, *O(0.25, 4.6, 3.8, -20), trans=0.9)
P.cam("8x por segundo", T_EM, *O(-0.95, 4.75, 4.6, 24), trans=1.0)
P.cam("rubis", T_RUB, *O(0, 3.9, 7.5, -20, .25), trans=1.1)
P.cam("corda cheia (afasta)", T_COM, *O(0, 3.4, 16, 22), trans=1.4)
P.cam("fecha", T_SEGUE - 1.0, *O(0, 3.3, 22, -12), trans=1.6)

# ---- rótulos em pílula (sempre na palavra falada) ----
def pill(txt, s, e, cor="pw", anchor=None, **kw):
    P.rot(txt, s, e, cor, anchor=anchor, **kw)
pill("0 BATERIA", at("bateria") - 0.05, at("E mesmo"), "pr", "dialTop", dy=-10)
pill("NÃO PARA", at("não para"), T_COMO, "py", "dialTop", dy=-10)
pill("MOLA REAL", at("uma mola"), at("Quando você"), "pw", "barrel", dy=-40)
pill("TAMBOR", at("tamborzinho"), at("Quando você"), "py", "barrelEdge", dy=60, dx=-40)
pill("COROA", at("coroa"), at("você aperta"), "py", "crown", dy=-20)
pill("MOLA APERTADA", at("aperta"), T_E_ALI, "pw", "barrel", dy=-40)
pill("ENERGIA GUARDADA", at("energia"), T_AMOLA, "py", "barrel", dy=-40)
pill("TAMBOR GIRA", at("gira o tambor"), at("que empurra"), "pw", "barrel", dy=-40)
pill("ENGRENAGENS", at("fila de engrenagens"), T_CADA, "py", "w4", dy=-40)
pill("+ RÁPIDO A CADA UMA", at("mais rápido"), at("no caminho"), "pw", "w4", dy=-40)
pill("PONTEIROS", at("ponteiros"), T_SOQUE, "py", "hand", dy=-30)
pill("SEM FREIO", T_SE, T_QUEM, "pr", None, x=540, y=430)
pill("ESCAPE", at("o escape"), T_UMA, "py", "escape", dy=-30)
pill("RODA DE ESCAPE", T_UMA, at("uma âncora"), "pw", "escape", dy=-30)
pill("ÂNCORA", at("âncora"), at("e um volante"), "py", "pallet", dy=-30)
pill("VOLANTE", at("volante"), at("o espiral"), "pw", "balance", dy=-30)
pill("ESPIRAL", at("o espiral"), T_ACADA, "py", "hair", dy=-60)
pill("1 DENTE POR VEZ", at("solta um dente"), T_ESSE, "py", "escape", dy=-30)
pill("TIC-TAC", at("tic-tac"), T_EM, "pr", "pallet", dy=-30)
pill("8x POR SEGUNDO", at("oito vezes"), T_RUB, "py", "balance", dy=-30)
pill("RUBIS SINTÉTICOS", at("rubis"), at("pra diminuir"), "pr", "ruby", dy=-30)
pill("MENOS ATRITO", at("atrito"), T_COM, "pw", "ruby", dy=-30)
pill("~40 HORAS", at("quarenta horas"), T_SEGUE, "py", "dialTop", dy=-10)
pill("SEGUE PRA VER POR DENTRO", T_SEGUE, DUR, "py", None, x=540, y=430)

HL = ["bateria", "andar", "dentro", "aco", "coroa", "energia", "soltar", "engrenagens", "rapido", "ponteiros", "problema",
      "instante", "escape", "gancho", "ancora", "volante", "espiral", "dente", "tictac", "oito", "rubis", "atrito", "quarenta"]

P.salvar(NAME, "Explicador 3D vertical", {
    "perfis": ["@peraexplica", "@explicandodireito.br", "@garagemexplicativa", "@thingsopened", "@oclaud1n"],
    "nota": "yt-dlp bloqueado no Instagram (sem login); estilo pelos prints do usuário: fundo escuro, objeto 3D central, pílulas de rótulo, legenda branca com palavra colorida"},
    "cena.js", dur=DUR)

# ---- camada visual do estilo 12 sobre o base.html compartilhado ----
ed = json.load(open(os.path.join(D, "edit.json"), encoding="utf-8"))
ed["fonts"] = {"Montserrat": "fonts/Montserrat-Black.ttf"}
ed["canvas"]["bg"] = "#0d0f15"
ed["build_script"] = "gerar_edit.py (palco.py + cena.js + _template-palco3d/base.html + camada CSS do estilo 12)"
for it in ed["items"]:
    if it["type"] == "caption":
        it["label"] = "Legenda grande (palavra destacada)"
        it["props"].update({"max_words": 3, "hl": HL})
json.dump(ed, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

CSS = """
#bc{left:50%!important;top:118px!important;transform:translateX(-50%);font-family:Montserrat,Arial,sans-serif!important;font-weight:900;font-size:34px!important;
 letter-spacing:.04em!important;color:#e6e8ef!important;text-transform:none!important;padding:10px 26px;border-radius:40px;background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.12)}
#chip{display:none!important}
#cap{background:none!important;border:none!important;box-shadow:none!important;top:1470px!important;max-width:1000px!important;padding:0!important;
 font-family:Montserrat,Arial,sans-serif!important;font-weight:900!important;font-size:96px!important;line-height:1.04!important;text-transform:uppercase;letter-spacing:-.015em!important}
#cap span{color:#fff!important;paint-order:stroke fill;-webkit-text-stroke:14px #000;text-shadow:0 8px 0 #000,0 0 30px rgba(0,0,0,.7)}
#cap span.hl{color:var(--hl,#FFD23F)!important}
.rot b{font-family:Montserrat,Arial,sans-serif;font-weight:900!important;font-size:50px!important;border-radius:999px!important;padding:14px 34px 16px!important;
 letter-spacing:.01em!important;box-shadow:0 10px 28px rgba(0,0,0,.55)}
.rot.pw b{background:#fff;color:#12131a}
.rot.py b{background:#FFD23F;color:#12131a}
.rot.pr b{background:#FF4D5E;color:#fff}
.rot.pw::after,.rot.py::after,.rot.pr::after{content:"";display:block;margin:0 auto;width:6px;height:46px;border-radius:3px;background:rgba(255,255,255,.85)}
.rot.py::after{background:#FFD23F}.rot.pr::after{background:#FF4D5E}
"""
t = open(os.path.join(D, "template.html"), encoding="utf-8").read()
rep = [
    ("</style>", CSS + "</style>"),
    ("let curG=-1, spans=[];",
     "const nrm=s=>s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^a-z0-9]/g,'');"
     "const HL=new Set((CAPI&&CAPI.props.hl)||[]);document.documentElement.style.setProperty('--hl',PARAM('cor_destaque','#FFD23F'));\nlet curG=-1, spans=[];"),
    ('s.textContent=(j?" ":"")+w.w; capEl.appendChild(s);', 's.textContent=(j?" ":"")+w.w; if(HL.has(nrm(w.w))) s.className="hl"; capEl.appendChild(s);'),
    ("y=clamp(y,380+d.offsetHeight,1540);", "y=clamp(y,230+d.offsetHeight,1330);"),
]
for a, b in rep:
    assert a in t, a
    t = t.replace(a, b, 1)
open(os.path.join(D, "template.html"), "w", encoding="utf-8").write(t)
print("camada estilo 12 ok")
