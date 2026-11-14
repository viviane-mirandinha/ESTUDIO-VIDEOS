"""Biblioteca para o gerar_edit.py dos vídeos do estilo "Saga sobrevivência 2D" — já traz o ritmo certo.

  import sys; sys.path.insert(0, r"<raiz>/kits/saga-2d"); from lib_edit import Video
  v = Video(__file__, nome="NN - DD-MM-AAAA - TITULO")        # lê words.json (tempos da fala) da pasta do vídeo
  v.cena_w(v.at("quatro"), "Água 4 L", fundo="#E0C49C", chao=1450, w=[
      dict(tipo="garrafa", x=330, y=1450, litros=4, t0=v.at("quatro"), t1=v.at("dia")),
      dict(tipo="rafa", x=760, y=1500, t0=0)], selos=[dict(texto="ÁGUA", x=540, y=330, t=v.at("agua"))])
  v.cena("radio", v.at("o"), "Rádio", {"sel": "..."}, {"net": v.at("internet")})   # cena antiga do template (SC.radio…)
  v.finalizar(extra_palavras_chave=[...], vermelho=[...], referencia={...}, pedido={...})   # grava edit.json e AVISA se o ritmo ficou fraco

Peças disponíveis (W.*): contador, garrafa, relogio, bateria, sinal, calendario, medidor, grafico, barra, pulso, carimbo, lista, rafa, selo.
Veja README.md. Todo tempo vem da fala (words.json): nunca invente segundo na mão.
"""
import json
import os
import re
import unicodedata

MAX_CENA = 3.8      # segundos: cena mais longa que isso tem que ser dividida em duas
CENAS_MIN = 16      # cortes por minuto (o modelo tem ~18)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


class Video:
    def __init__(self, arquivo, nome, words="words.json"):
        self.dir = os.path.dirname(os.path.abspath(arquivo))
        self.nome = nome
        self.words = json.load(open(os.path.join(self.dir, words), encoding="utf-8"))
        self.cur = -1.0
        self.cenas = []

    def at(self, p, ocorrencia=1, fim=False):
        """Segundo em que a palavra p (ou lista de alternativas) é falada, seguindo a ordem do roteiro."""
        alts = [norm(x) for x in (p if isinstance(p, list) else [p])]
        n = 0
        for w in self.words:
            if w["s"] < self.cur - 0.001:
                continue
            if norm(w["w"]) in alts:
                n += 1
                if n == ocorrencia:
                    self.cur = w["s"]
                    return round(w["e"] if fim else w["s"], 2)
        print("AVISO: palavra não achada:", p, "depois de", self.cur)
        self.cur += 0.4
        return round(self.cur, 2)

    def cena(self, cena, start, label, textos=None, t=None, spec=None):
        pr = {"cena": cena, "textos": textos or {}, "t": t or {}, "html": "", "fill": True}
        if spec:
            pr["spec"] = spec
        self.cenas.append({"start": max(0.0, round(start - 0.08, 2)) if start > 0 else 0.0, "label": label, "props": pr})

    def cena_w(self, start, label, w, fundo="#E0C49C", chao=None, chao_cor=None, selos=None, pan=None, escuro=None, base=None, textos=None, t=None):
        """Cena inteira só com peças animadas (sem desenhar SVG). base="prateleira"… usa uma cena antiga do template como fundo (com textos/t dela)."""
        spec = {"w": w}
        if base:
            spec["base"] = base
        if fundo and not base:
            spec["fundo"] = fundo
        elif fundo and base and fundo != "#E0C49C":
            spec["fundo"] = fundo
        if chao:
            spec["chao"] = chao
        if chao_cor:
            spec["chaoCor"] = chao_cor
        if selos:
            spec["selos"] = selos
        if pan:
            spec["pan"] = pan
        if escuro is not None:
            spec["escuro"] = escuro
        self.cena("widgets", start, label, textos=textos, t=t, spec=spec)

    def finalizar(self, extra_palavras_chave=(), vermelho=(), referencia=None, pedido=None, canvas=(1080, 1920),
                  fonts=None, estilo="Saga sobrevivência 2D (série)", cauda=3.2, per_group=3):
        fim_fala = round(self.words[-1]["e"] + 0.3, 2)
        dur = round(fim_fala + cauda, 2)
        items = []
        for i, c in enumerate(self.cenas):
            e = self.cenas[i + 1]["start"] if i + 1 < len(self.cenas) else dur
            items.append({"id": f"c{i + 1:02d}", "type": "html", "track": "fundo", "by": "template", "label": c["label"],
                          "start": c["start"], "dur": round(e - c["start"], 2), "props": c["props"]})
        items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": dur,
                      "props": {"words_file": "words.json", "per_group": per_group, "x": 540, "y": 1330, "size": 70, "font": "Oswald", "weight": 400,
                                "color": "#ffffff", "dim": "#ffffff", "hl_color": "#E8B23A", "bg": "rgba(12,12,12,.74)", "shadow": False,
                                "keywords": list(extra_palavras_chave)}})
        items.append({"id": "leg_vermelho", "type": "param", "label": "Legenda: palavras em vermelho", "props": {"value": ",".join(vermelho)}})
        # whoosh suave em todo 3º corte (nunca impact/pop)
        extra = [{"id": f"w{i}", "src": "whoosh.wav", "start": round(c["start"], 2), "volume": 0.12, "label": "whoosh"}
                 for i, c in enumerate(self.cenas[1:-1], 1) if i % 3 == 0] if os.path.exists(os.path.join(self.dir, "whoosh.wav")) else []
        audio = {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}}
        if extra:
            audio["extra"] = extra
        edit = {"version": 1, "name": self.nome, "estilo": estilo, "canvas": {"w": canvas[0], "h": canvas[1], "fps": 30, "bg": "#E9C9A0"},
                "duration": dur, "template": "local", "fonts": fonts or {"Oswald": "fonts/Oswald-Bold.ttf"},
                "referencia": referencia or {}, "pedido": pedido or {}, "audio": audio,
                "tracks": [{"id": "fundo", "name": "Cenas 2D"}, {"id": "legenda", "name": "Legenda"}], "items": items}
        json.dump(edit, open(os.path.join(self.dir, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        durs = [it["dur"] for it in items if it["type"] == "html"]
        print(f"cenas {len(durs)} | duração {dur}s | média {sum(durs) / len(durs):.1f}s | cortes/min {len(durs) * 60 / dur:.1f}")
        longas = [(it["id"], it["dur"]) for it in items if it["type"] == "html" and it["dur"] > MAX_CENA]
        if longas:
            print(f"AVISO: cenas acima de {MAX_CENA}s (divida em duas, cada uma com peça animada): {longas}")
        if len(durs) * 60 / dur < CENAS_MIN:
            print(f"AVISO: só {len(durs) * 60 / dur:.1f} cortes/min (mínimo {CENAS_MIN}). Faça mais cenas.")
        return edit
