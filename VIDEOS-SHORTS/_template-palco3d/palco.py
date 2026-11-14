# Biblioteca compartilhada dos shorts "palco 3D" (estilos 03/04).
# Tempo SEMPRE sai do words.json (whisper) alinhado ao texto exato do roteiro -> trocar voz = whisper + gerar_edit + render.
import json, os, re, unicodedata, difflib

HERE = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


class Projeto:
    def __init__(self, pasta, roteiro_txt):
        self.D = pasta
        wj = json.load(open(os.path.join(pasta, "words.json"), encoding="utf-8"))
        self.voz_dur = wj["duration"]
        ww = [w for w in wj["words"] if norm(w["w"])]
        texto = open(roteiro_txt, encoding="utf-8").read().strip()
        toks = texto.split()
        sn = [norm(t) for t in toks]
        wn = [norm(w["w"]) for w in ww]
        times = [None] * len(toks)
        sm = difflib.SequenceMatcher(None, sn, wn, autojunk=False)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == "equal":
                for k in range(a2 - a1):
                    times[a1 + k] = (ww[b1 + k]["s"], ww[b1 + k]["e"])
            elif op == "replace":
                s0, e0 = ww[b1]["s"], ww[b2 - 1]["e"]
                n = a2 - a1
                for k in range(n):
                    times[a1 + k] = (s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n)
        # buracos (palavra do roteiro que o whisper não ouviu): interpola
        for i in range(len(toks)):
            if times[i] is None:
                p = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
                q = next((times[j][0] for j in range(i + 1, len(toks)) if times[j]), p + 0.3)
                times[i] = (p, max(p + 0.05, min(q, p + 0.3)))
        self.words = [{"w": t, "s": round(a, 2), "e": round(b, 2)} for t, (a, b) in zip(toks, times)]
        self.sn = sn
        self.items = []

    # --- tempo pela fala ---
    def _find(self, frase, n):
        alvo = [norm(x) for x in frase.split() if norm(x)]
        hit = 0
        for i in range(len(self.sn) - len(alvo) + 1):
            if self.sn[i:i + len(alvo)] == alvo:
                hit += 1
                if hit == n:
                    return i, i + len(alvo) - 1
        raise KeyError(f"frase não achada no roteiro: {frase!r} #{n}")

    def at(self, frase, n=1):
        return self.words[self._find(frase, n)[0]]["s"]

    def end(self, frase, n=1):
        return self.words[self._find(frase, n)[1]]["e"]

    # --- itens ---
    def _it(self, d):
        d.setdefault("id", f"{d['track'][:3]}{len(self.items)}")
        self.items.append(d)
        return d

    def param(self, id, value, label):
        self.items.append({"id": id, "type": "param", "label": label, "props": {"value": value}})

    def chap(self, text, s, e):
        self._it({"type": "text", "track": "capitulo", "by": "template", "label": "• " + text,
                  "start": round(s, 2), "dur": round(e - s, 2), "props": {"text": text}})

    def cam(self, label, s, pos, look, trans=0.9, drift=0.35):
        self._it({"type": "html", "track": "camera", "by": "template", "label": "câmera: " + label,
                  "start": round(s, 2), "dur": 0.1, "props": {"html": "", "pos": pos, "look": look, "trans": trans, "drift": drift}})

    def stk(self, text, s, e, cor="amarelo", x=540, y=700, rot=-4, size=None):
        p = {"text": text, "cor": cor, "x": x, "y": y, "rot": rot}
        if size: p["size"] = size
        self._it({"type": "text", "track": "adesivos", "by": "template", "label": "adesivo: " + text,
                  "start": round(s, 2), "dur": round(e - s, 2), "props": p})

    def rot(self, text, s, e, estilo="branco", anchor=None, x=None, y=None, dx=0, dy=0, sub=None, size=None, **kw):
        p = {"text": text, "estilo": estilo, "dx": dx, "dy": dy}
        if anchor: p["anchor"] = anchor
        if x is not None: p["x"] = x
        if y is not None: p["y"] = y
        if sub: p["sub"] = sub
        if size: p["size"] = size
        p.update(kw)
        self._it({"type": "text", "track": "rotulos", "by": "template", "label": "rótulo: " + text,
                  "start": round(s, 2), "dur": round(e - s, 2), "props": p})

    def cena(self, label, s, e, id=None, **props):
        props.setdefault("html", "")
        d = {"type": "html", "track": "cena", "by": "template", "label": "3D: " + label,
             "start": round(s, 2), "dur": round(e - s, 2), "props": props}
        if id: d["id"] = id
        return self._it(d)

    def salvar(self, name, estilo, referencia, cena_js, dur=None, extra_params=()):
        DUR = round(dur or (self.voz_dur + 0.6), 2)
        cap = {"id": "legenda", "type": "caption", "track": "legenda", "by": "template", "label": "Legenda karaokê",
               "start": 0, "dur": DUR, "props": {"words": self.words, "max_words": 5}}
        edit = {
            "version": 1, "name": name,
            "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0b0c10"},
            "duration": DUR, "template": "local",
            "grupo": "ESTILOS SHORTS", "estilo": estilo, "referencia": referencia,
            "fonts": {"Inter": "fonts/Inter.ttf"},
            "build_script": "gerar_edit.py (palco.py + cena.js + _template-palco3d/base.html)",
            "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
            "tracks": [{"id": "cena", "name": "Cenas 3D"}, {"id": "camera", "name": "Câmera"},
                       {"id": "rotulos", "name": "Rótulos/valores"}, {"id": "adesivos", "name": "Adesivos"},
                       {"id": "capitulo", "name": "Capítulo (chip)"}, {"id": "legenda", "name": "Legenda"}],
            "items": self.items + [cap],
        }
        json.dump(edit, open(os.path.join(self.D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        base = open(os.path.join(HERE, "base.html"), encoding="utf-8").read()
        js = open(os.path.join(self.D, cena_js), encoding="utf-8").read()
        open(os.path.join(self.D, "template.html"), "w", encoding="utf-8").write(base.replace("/*__CENA__*/", js))
        print("edit.json ok", DUR, "s,", len(self.items), "itens")
        return DUR
