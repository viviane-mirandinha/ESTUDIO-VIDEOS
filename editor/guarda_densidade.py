"""guarda_densidade.py — Guarda de densidade de gráficos (não deixa virar poluição de animação).

Feito do zero pro painel (nada do Auto B-Roll Studio). Reimplementa a IDEIA de um "density guard":
mede quanto do vídeo é gráfico/animação por cima e DERRUBA o excesso quando as "Suas regras" pedem
("máx. 1 animação a cada N s", "sem animações", "no máx. X% de gráfico"). A legenda (fala) e a
mídia de base (foto/vídeo) nunca são tocadas — só os gráficos DECORATIVOS (textos, cartões, blocos).

Classificação (agnóstica de estilo):
  - legenda       -> type "caption"  (é a fala; nunca conta nem derruba)
  - gráfico decor -> type "text" / "html" / "bloco"  (conta e pode derrubar)
  - mídia de base -> type "image" / "video" / "scene"  (o footage; nunca derruba)
Rosto não dá pra medir pelo edit.json, então o % de rosto não é checado aqui (fica pro editor de
vídeo falado medir no render, se um dia precisar).

Regras: vêm de edit["regras"] — pode ser um dict {max_pct, intervalo_min, respiro, sem_animacao,
strict} e/ou uma lista de frases (chips). Frases reconhecidas: "sem animaç…", "máx 1 … a cada N s/seg",
"no máximo X%". Sem regras = não mexe em nada.

Uso:
  python guarda_densidade.py <pasta>            # mede e imprime
  python guarda_densidade.py <pasta> --aplicar  # derruba o excesso no edit.json (guarda .bak-densidade)
  python guarda_densidade.py <pasta> --json
"""
import copy
import json
import re
import sys
from pathlib import Path

GRAF_DECOR = ("text", "html", "bloco")
LEGENDA = ("caption",)
MIDIA = ("image", "video", "scene")

PADRAO = {"max_pct": 25, "intervalo_min": 7.0, "respiro": 1.5, "sem_animacao": False, "strict": False, "broll_primeiro": False}


def _num(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d


def _ativos(edit):
    """Itens que valem (não escondidos, não param/legacy/template-base)."""
    for it in edit.get("items", []):
        if it.get("hidden") or it.get("type") in ("param", "legacy"):
            continue
        yield it


def _graficos(edit):
    gs = []
    for it in _ativos(edit):
        if it.get("type") in GRAF_DECOR:
            s = _num(it.get("start"))
            d = max(0.04, _num(it.get("dur"), 1))
            gs.append({"it": it, "id": it.get("id"), "inicio": s, "fim": s + d, "dur": d})
    gs.sort(key=lambda x: x["inicio"])
    return gs


def _cobertura(gs):
    """Segundos cobertos por gráfico (união dos intervalos, sem contar sobreposição em dobro)."""
    tot, fim_ant = 0.0, -1.0
    for g in sorted(gs, key=lambda x: x["inicio"]):
        a, b = max(g["inicio"], fim_ant), g["fim"]
        if b > a:
            tot += b - a
            fim_ant = b
        elif g["fim"] > fim_ant:
            fim_ant = g["fim"]
    return tot


def regras_densidade(edit):
    """Lê edit['regras'] (dict e/ou lista de frases). Devolve dict de regras ou None se não houver."""
    r = edit.get("regras")
    if not r:
        return None
    reg = dict(PADRAO)
    frases = []
    if isinstance(r, dict):
        for k in PADRAO:
            if k in r:
                reg[k] = r[k]
        frases = r.get("chips") or r.get("frases") or []
    elif isinstance(r, (list, tuple)):
        frases = list(r)
    elif isinstance(r, str):
        frases = [r]
    if reg.get("broll_primeiro") and not (isinstance(r, dict) and ("intervalo_min" in r or "max_pct" in r)):
        reg["intervalo_min"], reg["max_pct"] = 10.0, 15.0   # "B-roll primeiro": gráfico só de vez em quando (1 a cada 10 s, até 15%)
    texto = " ".join(str(f) for f in frases).lower()
    if re.search(r"sem anima|nada de anima|zero anima|sem gr[áa]fico", texto):
        reg["sem_animacao"] = True
    m = re.search(r"m[áa]x.{0,12}?(\d+).{0,6}?(?:anima|gr[áa]fico).{0,20}?a cada\s*(\d+)\s*(?:s|seg)", texto) \
        or re.search(r"(?:1|uma).{0,16}?(?:anima|gr[áa]fico).{0,16}?a cada\s*(\d+)\s*(?:s|seg)", texto)
    if m:
        reg["intervalo_min"] = float(m.group(m.lastindex))
    m = re.search(r"(?:no m[áa]ximo|m[áa]x\.?)\s*(\d{1,2})\s*%\s*(?:de\s*)?gr[áa]fico", texto)
    if m:
        reg["max_pct"] = float(m.group(1))
    return reg


def medir(edit):
    dur = _num(edit.get("duration")) or (max((_num(i.get("start")) + _num(i.get("dur"), 0)
                                               for i in _ativos(edit)), default=0))
    gs = _graficos(edit)
    cob = _cobertura(gs)
    menor = None
    for a, b in zip(gs, gs[1:]):
        gap = b["inicio"] - a["inicio"]
        menor = gap if menor is None else min(menor, gap)
    colados = sum(1 for a, b in zip(gs, gs[1:]) if b["inicio"] - a["fim"] < PADRAO["respiro"] - 0.01)
    return {"duracao": round(dur, 2), "n_graficos": len(gs),
            "pct_grafico": round(100 * cob / dur, 1) if dur else 0,
            "segundos_grafico": round(cob, 1),
            "menor_intervalo": round(menor, 2) if menor is not None else None,
            "colados": colados}


def _importante(it):
    """Gráfico que não deve ser derrubado: marcado à mão, ou que mostra número/palavra-chave."""
    if it.get("manter") or it.get("keep") or it.get("fixar"):
        return True
    p = it.get("props", {})
    txt = " ".join(str(p.get(k, "")) for k in ("text", "texto", "valor", "value", "titulo"))
    return bool(re.search(r"\d", txt))   # número quase sempre é informação, não decoração


def aplicar(edit, regras=None, marcar=True):
    """Derruba (hidden=True) os gráficos decorativos que estouram as regras. Reversível.
    Devolve (edit, derrubados[])."""
    regras = regras or regras_densidade(edit)
    if not regras:
        return edit, []
    dur = _num(edit.get("duration")) or 0
    gs = _graficos(edit)
    if not gs:
        return edit, []
    derrubados = []

    def derruba(g, motivo):
        if marcar:
            g["it"]["hidden"] = True
            g["it"]["_densidade"] = motivo
        derrubados.append({"id": g["id"], "inicio": round(g["inicio"], 2), "motivo": motivo})

    if regras.get("sem_animacao"):
        for g in gs:
            if not _importante(g["it"]):
                derruba(g, "sem animações (sua regra)")
        return edit, derrubados

    # 1) intervalo mínimo + respiro: varre em ordem, mantém o 1º (gancho) e os importantes
    intervalo = float(regras.get("intervalo_min", PADRAO["intervalo_min"]))
    respiro = float(regras.get("respiro", PADRAO["respiro"]))
    ultimo = None
    vivos = []
    for g in gs:
        if ultimo is None or _importante(g["it"]) \
           or (g["inicio"] - ultimo["inicio"] >= intervalo and g["inicio"] - ultimo["fim"] >= respiro):
            vivos.append(g)
            ultimo = g
        else:
            derruba(g, f"muito perto do gráfico anterior (regra: 1 a cada {intervalo:.0f}s)")

    # 2) teto de porcentagem: se ainda passar, derruba os últimos não-importantes
    maxpct = float(regras.get("max_pct", PADRAO["max_pct"]))
    if dur:
        i = len(vivos) - 1
        while 100 * _cobertura(vivos) / dur > maxpct and i >= 0:
            g = vivos[i]
            if not _importante(g["it"]) and not (g is vivos[0]):
                derruba(g, f"passou do limite de {maxpct:.0f}% de gráfico")
                vivos.pop(i)
            i -= 1
    return edit, derrubados


def filtrar_para_render(edit):
    """Usado pelo build: devolve uma CÓPIA com o excesso escondido (não grava em disco)."""
    if not edit.get("regras"):
        return edit
    e = copy.deepcopy(edit)
    aplicar(e, marcar=True)
    return e


def aplicar_em_disco(proj):
    proj = Path(proj)
    editp = proj / "edit.json"
    edit = json.loads(editp.read_text(encoding="utf-8-sig"))
    antes = medir(edit)
    _, derrubados = aplicar(edit, marcar=True)
    if derrubados:
        bak = editp.with_suffix(".json.bak-densidade")
        if not bak.exists():
            bak.write_text(editp.read_text(encoding="utf-8-sig"), encoding="utf-8")
        editp.write_text(json.dumps(edit, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"antes": antes, "depois": medir(edit), "derrubados": derrubados}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    proj = Path(args[0])
    edit = json.loads((proj / "edit.json").read_text(encoding="utf-8-sig"))
    if "--aplicar" in sys.argv:
        res = aplicar_em_disco(proj)
        if "--json" in sys.argv:
            print(json.dumps(res, ensure_ascii=False))
        else:
            print(f"Gráfico antes: {res['antes']['pct_grafico']}%  →  depois: {res['depois']['pct_grafico']}%")
            for d in res["derrubados"]:
                print(f"  - derrubado {d['id']} @ {d['inicio']}s — {d['motivo']}")
            if not res["derrubados"]:
                print("Nada pra derrubar (dentro das regras, ou sem regras).")
        return
    m = medir(edit)
    reg = regras_densidade(edit)
    if "--json" in sys.argv:
        print(json.dumps({"medida": m, "regras": reg}, ensure_ascii=False))
    else:
        print(f"Duração {m['duracao']}s · {m['n_graficos']} gráficos · {m['pct_grafico']}% da tela · "
              f"menor intervalo {m['menor_intervalo']}s · {m['colados']} colados")
        print("Regras ligadas:" if reg else "Sem 'Suas regras' neste vídeo.", reg or "")


if __name__ == "__main__":
    main()
