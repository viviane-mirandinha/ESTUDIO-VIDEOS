# Gera edit.json do vídeo 13 (futebol stats rápido). Tempos vêm do words.json (faster-whisper),
# texto da legenda vem do roteiro.txt (alinhado com difflib).
import json, re, difflib
from pathlib import Path
P = Path(__file__).parent
W = json.load(open(P / "words.json", encoding="utf-8"))["words"]
rot = re.findall(r"\S+", (P / "roteiro.txt").read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"[^\wà-ú]", "", s.lower())
sm = difflib.SequenceMatcher(a=[norm(x["w"]) for x in W], b=[norm(x) for x in rot], autojunk=False)
words = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal" or (i2 - i1) == (j2 - j1):
        for k in range(i2 - i1):
            words.append({"w": rot[j1 + k], "s": W[i1 + k]["s"], "e": W[i1 + k]["e"]})
    elif i2 > i1 and j2 > j1:  # junta/espalha
        s, e = W[i1]["s"], W[i2 - 1]["e"]
        n = j2 - j1
        for k in range(n):
            words.append({"w": rot[j1 + k], "s": round(s + (e - s) * k / n, 2), "e": round(s + (e - s) * (k + 1) / n, 2)})
    elif j2 > j1:  # palavra do roteiro sem tempo: gruda na anterior
        for k in range(j2 - j1):
            t = words[-1]["e"] if words else 0
            words.append({"w": rot[j1 + k], "s": t, "e": t})
DUR = round(W[-1]["e"] + 1.6, 2)

def T(i):  # início da palavra i (índice do whisper)
    return W[i]["s"]

PEL, MAR = "#39FF6A", "#3EC8FF"
cenas = [
    dict(id="c0", label="Gancho: Pelé vs Maradona", tipo="abertura", start=0, end=4.2,
         titulo="PELÉ VS MARADONA", t_vs=T(2), selo1="SÓ NÚMEROS", t_s1=T(3), selo2="SEM OPINIÃO", t_s2=T(5)),
    dict(id="c1", label="Copas do Mundo 3 x 1", tipo="duelo", start=4.2, end=9.3, titulo="COPAS DO MUNDO", icone="taca",
         a=dict(valor=3, t=T(11), sub="1958 · 1962 · 1970", ts=T(11) + .5),
         b=dict(valor=1, t=T(13), sub="1986", ts=T(13) + .4)),
    dict(id="c2", label="Gols em Copas 12 x 8", tipo="duelo", start=9.3, end=16.3, titulo="GOLS EM COPAS",
         a=dict(valor=12, t=T(19), sub="EM 14 JOGOS", ts=T(21)),
         b=dict(valor=8, t=T(24), sub="EM 21 JOGOS", ts=T(26)),
         barra=dict(rotulo="GOLS POR JOGO", a="0,86", b="0,38", va=12 / 14, vb=8 / 21, t=T(26) + .3)),
    dict(id="c3", label="Gols pela seleção 77 x 34", tipo="duelo", start=16.3, end=22.4, titulo="GOLS PELA SELEÇÃO",
         a=dict(valor=77, t=T(33), sub="EM 92 JOGOS", ts=T(35)),
         b=dict(valor=34, t=T(37), sub="EM 91 JOGOS", ts=T(39)),
         barra=dict(rotulo="GOLS", a="77", b="34", va=77, vb=34, t=T(37))),
    dict(id="c4", label="Gols por um clube 643 x 115", tipo="duelo", start=22.4, end=32.5, titulo="GOLS POR UM CLUBE",
         a=dict(valor=643, t=T(46), t1=T(52), sub="SANTOS", ts=T(52)),
         b=dict(valor=115, t=T(54), t1=T(58), sub="NAPOLI", ts=T(58)),
         barra=dict(rotulo="GOLS", a="643", b="115", va=643, vb=115, t=T(54)),
         selo="MAIOR ARTILHEIRO DO NAPOLI POR +20 ANOS", t_selo=T(62)),
    dict(id="c5", label="1.279 gols (Guinness)", tipo="solo", start=32.5, end=37.0, lado="a", titulo="GOLS NA CARREIRA",
         valor=1279, t=T(75), t1=T(81), selo="RECORDE GUINNESS", t_selo=T(73), sub="PELÉ · 1.363 JOGOS", ts=T(82)),
    dict(id="c6", label="Gol do século (FIFA 2002)", tipo="solo", start=37.0, end=41.7, lado="b", titulo="O GOL DO SÉCULO",
         t_tit=T(89), selo="VOTAÇÃO DA FIFA · 2002", t_selo=T(96), sub="MÉXICO 1986 · VS INGLATERRA", ts=T(98)),
    dict(id="c7", label="Jogador do século: os dois", tipo="divide", start=41.7, end=46.6, titulo="JOGADOR DO SÉCULO",
         t_tit=T(113), selo="FIFA · 2000", t_selo=T(105), selo2="OS DOIS", t_s2=T(116)),
    dict(id="c8", label="Placar final + CTA", tipo="final", start=46.6, end=DUR, titulo="PLACAR DOS NÚMEROS",
         placar_a=4, placar_b=0, t_placar=T(119), pergunta="QUEM FOI O MAIOR?", t_perg=T(125), cta="COMENTA AÍ", t_cta=T(129)),
]
items = [
    {"id": "cor_a", "type": "param", "label": "Cor do Pelé (neon)", "props": {"value": PEL}},
    {"id": "cor_b", "type": "param", "label": "Cor do Maradona (neon)", "props": {"value": MAR}},
    {"id": "cor_destaque", "type": "param", "label": "Cor de destaque", "props": {"value": "#FFE600"}},
    {"id": "nome_a", "type": "param", "label": "Nome lado esquerdo", "props": {"value": "PELÉ"}},
    {"id": "nome_b", "type": "param", "label": "Nome lado direito", "props": {"value": "MARADONA"}},
]
for c in cenas:
    s, e = c.pop("start"), c.pop("end")
    items.append({"id": c.pop("id"), "type": "html", "track": "cenas", "label": c.pop("label"), "by": "template",
                  "start": round(s, 2), "dur": round(e - s, 2), "props": c})
items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda 2 palavras", "by": "template",
              "start": 0, "dur": DUR, "props": {"words": words, "per_group": 2, "y": 1690, "size": 92,
              "keywords": ["PELÉ", "MARADONA", "TRÊS", "UMA", "DOZE", "OITO", "SETENTA", "TRINTA", "SEISCENTOS",
                           "CENTO", "MIL", "GUINNESS", "SÉCULO", "FIFA", "MAIOR", "COMENTA"]}})
edit = {
    "version": 1, "name": "13 - 24-10-2026 - FUTEBOL STATS RAPIDO - Pele vs Maradona em numeros",
    "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#05060a"}, "duration": DUR, "template": "local",
    "grupo": "ESTILOS SHORTS", "estilo": "Futebol stats rápido (prime/punch neon)",
    "referencia": {"canal": "Factual Animation - Ultimate Football Stats Channel",
                   "canal_url": "https://www.youtube.com/@FactualAnimation",
                   "video": "https://youtu.be/uUEM5TCjsAg",
                   "titulo": "Messi vs Ronaldo: Who is BETTER in Big Games? - Stats Comparison",
                   "nota": "estrutura lado a lado (jogador | VS + categoria | jogador, número embaixo de cada um). 2ª ref de ritmo: Football Daily https://youtu.be/xOToL-SSkKI. Sem fotos, sem logo, sem nome dos canais; visual punch/neon pedido pelo gênero."},
    "fonts": {"Anton": "fonts/Anton-Regular.ttf", "Barlow": "fonts/BarlowCondensed-Bold.ttf"},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.16, "start": 0, "fade_out": 1.5, "duck": True},
              "extra": [{"id": f"w{i}", "src": "sfx/whoosh.wav", "start": round(t - 0.12, 2), "volume": 0.22, "label": "whoosh"}
                        for i, t in enumerate([4.2, 16.3, 32.5, 41.7, 46.6])]},
    "tracks": [{"id": "cenas", "name": "Cenas (template)"}, {"id": "legenda", "name": "Legenda"}],
    "items": items,
}
json.dump(edit, open(P / "edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", DUR, len(words), " ".join(x["w"] for x in words[115:]))
