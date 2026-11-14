# gera edit.json (template local) do vídeo 04 — tempos tirados do words.json
import json
from pathlib import Path
P = Path(__file__).parent
DUR = 51.6
def T(id, label, start, dur, text, **kw):
    return {"id": id, "type": "text", "track": "textos", "label": label, "start": start, "dur": dur, "by": "template",
            "props": dict(text=text, **kw)}
def A(i, nome, start, dur, valor, dec, valor_em, img, alt, vel, anim, info, status="VELOCIDADE MÁXIMA", conf="ALTA"):
    return {"id": f"a{i}", "type": "text", "track": "visual", "label": f"{i} · {nome}", "start": start, "dur": dur, "by": "template",
            "props": {"text": nome, "valor": valor, "dec": dec, "unidade": "km/h", "valor_em": valor_em, "img": img,
                      "alt": alt, "vel": vel, "anim": anim, "status": status, "conf": conf, "info": info}}
items = [
    T("t_titulo1", "Título 1", 0.1, 4.5, "A VELOCIDADE DOS ANIMAIS", size=60, color="#ffffff"),
    T("t_titulo2", "Título 2 (vermelho)", 2.26, 2.35, "DO MAIS LENTO AO MAIS RÁPIDO", size=64, color="#e5262a"),
    T("t_passa", "Guepardo passando (intro)", 5.7, 1.8, "GUEPARDO", valor="IMBATÍVEL?", img="img/guepardo.png"),
    T("t_rei", "Frase do rei", 8.45, 2.8, "O REI NÃO CORRE NO CHÃO", size=58, color="#ffffff", img="img/falcao_voo.png"),
    A(1, "LESMA DE JARDIM", 13.02, 4.76, 0.05, 2, 14.88, "img/lesma.png", 150, 16, "slide", "RASTEJA SOBRE MUCO"),
    A(2, "TARTARUGA-GIGANTE", 17.78, 3.12, 0.3, 1, 19.5, "img/tartaruga.png", 210, 40, "walk", "PASSO DE 250 KG"),
    A(3, "HOMEM MÉDIO", 20.9, 2.58, 24, 0, 22.3, "img/homem.png", 300, 220, "run", "CORRIDA CURTA", conf="MÉDIA"),
    A(4, "GATO DOMÉSTICO", 23.48, 2.66, 48, 0, 24.72, "img/gato.png", 165, 380, "gallop", "ARRANCADA CURTA"),
    A(5, "ANTÍLOPE-AMERICANO", 26.14, 2.96, 89, 0, 27.68, "img/antilope.png", 190, 600, "bound", "MANTÉM POR QUILÔMETROS"),
    A(6, "GUEPARDO", 29.1, 4.32, 120, 0, 32.1, "img/guepardo.png", 215, 850, "sprint", "REI DO SOLO · 20 S DE FÔLEGO"),
    A(7, "FALCÃO-PEREGRINO", 33.42, 9.7, 380, 0, 36.22, "img/falcao.png", 300, 0, "dive", "EM PICADA (MERGULHO)", status="MERGULHO"),
    T("t_x3", "Comparação 3×", 38.0, 2.65, "3× MAIS RÁPIDO", size=64, color="#ffffff",
      a="GUEPARDO", va=120, b="FALCÃO", vb=380),
    T("t_grav", "Gravidade", 40.76, 2.35, "GRAVIDADE > MÚSCULO", size=60, color="#ffffff"),
    T("t_rank", "Ranking final", 43.1, 8.5, "RANKING DA VELOCIDADE", size=52, color="#ffffff"),
    T("t_inscreva", "Botão inscreva-se", 45.25, 6.3, "INSCREVA-SE", size=52, color="#ffffff", bg="#e5262a"),
    T("t_prox", "Próximo vídeo", 46.3, 5.3, "PRÓXIMO: QUEM ACELERA MAIS QUE UM F1?", size=48, color="#ffffff"),
]
edit = {
    "version": 1, "name": "04 - COMPARACAO RANKING - Do mais lento ao mais rápido",
    "estilo": "Comparação / ranking animado (RED SIDE)",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#7fb6e6"}, "duration": DUR, "template": "local",
    "referencia": {"canal": "RED SIDE", "canal_url": "https://www.youtube.com/@redsideofficial",
                   "video": "https://youtu.be/3wVvwd4oI1Y", "titulo": "corrida de personagens por velocidade",
                   "nota": "versão 2D/2.5D: parallax + recortes PNG + rótulo vermelho fixo"},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
              "extra": [{"id": "w1", "src": "sfx/whoosh.wav", "start": 5.75, "volume": 0.18, "label": "whoosh guepardo"},
                        {"id": "w2", "src": "sfx/whoosh.wav", "start": 33.45, "volume": 0.22, "label": "whoosh mergulho"}]},
    "tracks": [{"id": "fundo", "name": "Cenas"}, {"id": "visual", "name": "Animais"}, {"id": "textos", "name": "Textos"}],
    "items": items,
}
json.dump(edit, open(P / "edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(items))
