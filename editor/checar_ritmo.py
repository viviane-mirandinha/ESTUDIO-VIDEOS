"""Guarda de qualidade dos vídeos pedidos pelo painel: confere RITMO, ANIMAÇÃO e FIDELIDADE antes de entregar.

  python editor/checar_ritmo.py <pasta_do_video> [--final]

  Sai com código 0 = ok, 2 = tem ERRO (o build_from_edit.py recusa renderizar a 1ª versão até corrigir).
  --final também exige final.mp4 + sheet.jpg + DECISOES.md (rode depois do render).
O alvo vem do MODELO do estilo (PEDIDO.md → "Onde está o modelo do estilo"): o vídeo novo não pode ser mais lento nem
mais seco que o modelo. O que checa:
  1. template certo (nunca "generic" se o modelo é um template próprio)
  2. cortes por minuto, duração média e cena mais longa em relação ao modelo
  3. cada cena tem um elemento ANIMADO que mostra o dado (contador, nível, ponteiro, risco, linha desenhando…)
  4. narração fiel ao roteiro aprovado (palavra por palavra)
  5. som: sem impact/pop; whoosh nos cortes
  6. DECISOES.md explica o que foi trocado (voz, etc.)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path


def _json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn"))
    return re.sub(r"[^a-z0-9 ]", "", s)


def _cenas(edit):
    return [i for i in (edit or {}).get("items", []) if i.get("type") == "html" and i.get("by") == "template"]


def _stats(edit):
    cs = _cenas(edit)
    if not cs:  # template "generic": todos os itens visuais
        cs = [i for i in (edit or {}).get("items", []) if i.get("type") in ("image", "scene", "video", "html") and i.get("dur")]
    ds = [float(i["dur"]) for i in cs if float(i.get("dur") or 0) > 0]
    dur = float((edit or {}).get("duration") or sum(ds) or 1)
    if not ds:
        return None
    return {"n": len(ds), "cpm": len(ds) * 60 / dur, "media": sum(ds) / len(ds), "max": max(ds)}


# ---- cena "dinâmica" = tem movimento que mostra um dado (não só aparecer) ----
_SINAIS_DADO = ("onUpdate", "attr:", "rotation:", "strokeDashoffset", "stagger", "fill:", "scaleY", "scaleX", "for (", "repeat:")
_TIPOS_ANIM = {"contador", "garrafa", "relogio", "bateria", "sinal", "calendario", "medidor", "grafico", "barra", "pulso", "lista", "carimbo"}


def _blocos_template(html):
    blocos = {}
    marcas = [(m.start(), m.group(1)) for m in re.finditer(r"^SC\.(\w+)\s*=", html, flags=re.M)]
    fim_total = html.find("/* ---------------- montagem")
    fim_total = fim_total if fim_total > 0 else len(html)
    for i, (pos, nome) in enumerate(marcas):
        fim = marcas[i + 1][0] if i + 1 < len(marcas) else fim_total
        blocos[nome] = html[pos:min(fim, fim_total)]
    return blocos


def _cena_dinamica(item, blocos):
    """Elemento animado que mostra o DADO (contador, nível, ponteiro, risco, linha desenhando…)."""
    pr = item.get("props") or {}
    nome = pr.get("cena")
    if nome == "widgets":
        ws = [w.get("tipo") for w in (pr.get("spec") or {}).get("w", [])]
        return any(t in _TIPOS_ANIM for t in ws)
    b = blocos.get(nome, "")
    if "W." in b and any(f"W.{t}" in b for t in _TIPOS_ANIM):
        return True
    anim = b[b.find("anim()"):] if "anim()" in b else ""
    return sum(1 for s in _SINAIS_DADO if s in anim) >= 1 and len(re.findall(r"tl\.(?:fromTo|to)\(", anim)) >= 1


def _cena_movimento(item, blocos):
    """Qualquer movimento além de só 'aparecer' (personagem, câmera, deslizar, girar…)."""
    if _cena_dinamica(item, blocos):
        return True
    b = blocos.get((item.get("props") or {}).get("cena"), "")
    anim = b[b.find("anim()"):] if "anim()" in b else ""
    return len(re.findall(r"tl\.(?:fromTo|to)\(|idleRafa|bobY|shake\(|fall\(", anim)) >= 1


def _roteiro_pedido(txt):
    m = re.search(r"^## Roteiro APROVADO[^\n]*\n(.*?)(?=^## )", txt, flags=re.M | re.S)
    if not m:
        return ""
    return " ".join(l for l in m.group(1).splitlines() if l.strip() and not l.lstrip().startswith(">"))


def checar(pasta, final=False):
    p = Path(pasta)
    erros, avisos, infos = [], [], []
    edit = _json(p / "edit.json")
    if not edit:
        return ["não achei/não consegui ler o edit.json"], [], []
    ped = (p / "PEDIDO.md").read_text(encoding="utf-8", errors="replace") if (p / "PEDIDO.md").exists() else ""
    modelo = None
    m = re.search(r"modelo do estilo:\s*`([^`]+)`", ped)
    if m and (Path(m.group(1)) / "edit.json").exists():
        modelo = Path(m.group(1))
    medit = _json(modelo / "edit.json") if modelo else None

    # 1. template
    tm = (medit or {}).get("template")
    if tm and tm != "generic" and edit.get("template") != tm:
        erros.append(f"template errado: o modelo usa \"{tm}\" e o vídeo usa \"{edit.get('template')}\" (é proibido simplificar o estilo)")

    # 2. ritmo
    vs, ms = _stats(edit), _stats(medit)
    if vs:
        lim_cpm = 0.85 * ms["cpm"] if ms else 14.0
        lim_med = 1.2 * ms["media"] if ms else 4.2
        lim_max = max(ms["max"] + 0.5, 4.5) if ms else 6.0
        infos.append(f"ritmo: {vs['n']} cenas | {vs['cpm']:.1f} cortes/min (mín {lim_cpm:.1f}) | média {vs['media']:.1f}s (máx {lim_med:.1f}s) | maior cena {vs['max']:.1f}s (máx {lim_max:.1f}s)")
        if vs["cpm"] < lim_cpm:
            ref = f", o modelo tem {ms['cpm']:.1f}" if ms else ""
            erros.append(f"poucos cortes: {vs['cpm']:.1f}/min (mínimo {lim_cpm:.1f}{ref}). Divida as cenas longas em duas ou mais")
        if vs["media"] > lim_med:
            erros.append(f"cenas longas demais em média ({vs['media']:.1f}s; máximo {lim_med:.1f}s)")
        longas = [f"{i['id']} ({float(i['dur']):.1f}s)" for i in (_cenas(edit) or []) if float(i["dur"]) > lim_max]
        if longas:
            erros.append(f"cena(s) longa(s) demais (> {lim_max:.1f}s): {', '.join(longas)} — divida em duas, cada uma com peça animada")

    # 3. animação por cena (só estilos com template próprio que tenha cenas SC.*)
    tmpl = p / "template.html"
    cs = _cenas(edit)
    if cs and tmpl.exists():
        blocos = _blocos_template(tmpl.read_text(encoding="utf-8", errors="replace"))
        mortas = [f"{i['id']} ({(i.get('props') or {}).get('cena')})" for i in cs if not _cena_dinamica(i, blocos)]
        paradas = [f"{i['id']} ({(i.get('props') or {}).get('cena')})" for i in cs if not _cena_movimento(i, blocos)]
        frac = 1 - len(mortas) / len(cs)
        infos.append(f"animação: {len(cs) - len(mortas)}/{len(cs)} cenas com elemento animado do dado | {len(cs) - len(paradas)}/{len(cs)} com algum movimento")
        if frac < 0.6:
            erros.append(f"{len(mortas)} de {len(cs)} cenas não têm elemento animado que mostre o dado (mínimo 60% das cenas): {', '.join(mortas[:14])}"
                         " — use as peças de kits/saga-2d/widgets.js (garrafa, relogio, bateria, sinal, calendario, medidor, grafico, barra, contador, lista…)")
        elif mortas:
            avisos.append(f"cenas sem elemento animado do dado: {', '.join(mortas)}")
        if len(paradas) > max(1, len(cs) // 10):
            erros.append(f"cenas totalmente paradas (só aparecem, nada se mexe): {', '.join(paradas)}")
    elif cs and not tmpl.exists():
        erros.append("template.html não está na pasta do vídeo (copie o do modelo)")

    # 4. roteiro fiel
    rot, nar = _roteiro_pedido(ped), ""
    if (p / "narracao.txt").exists():
        nar = (p / "narracao.txt").read_text(encoding="utf-8", errors="replace")
    if rot:
        if not nar:
            erros.append("narracao.txt não existe (a narração tem que ser o roteiro aprovado, palavra por palavra)")
        else:
            a, b = _norm(rot).split(), _norm(nar).split()
            if a != b:
                import difflib
                r = difflib.SequenceMatcher(None, a, b).ratio()
                (erros if r < 0.97 else avisos).append(f"narração difere do roteiro aprovado (similaridade {r:.0%}) — texto fixo, não reescreva")

    # 5. som
    ex = (edit.get("audio") or {}).get("extra") or []
    ruins = [x.get("src", "") for x in ex if re.search(r"impact|pop", str(x.get("src", "")) + str(x.get("label", "")), re.I)]
    if ruins:
        erros.append(f"som proibido (impact/pop): {ruins}")
    if cs and len(ex) < max(3, len(cs) // 4):
        avisos.append(f"poucos whooshes ({len(ex)}): ponha um whoosh suave (volume ~0.12) em cerca de metade dos cortes")

    # 6. DECISOES.md
    if final or (p / "final.mp4").exists():
        for n in ("final.mp4", "sheet.jpg", "DECISOES.md"):
            if not (p / n).exists():
                erros.append(f"falta {n} (gere o contact-sheet com ffmpeg e anote as decisões)")
    if (p / "DECISOES.md").exists() and re.search(r"fish", ped, re.I):
        d = (p / "DECISOES.md").read_text(encoding="utf-8", errors="replace").lower()
        if "voz" not in d:
            avisos.append("DECISOES.md não fala da voz (a voz pedida foi usada? se não, explique)")
    return erros, avisos, infos


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    pasta = sys.argv[1]
    erros, avisos, infos = checar(pasta, "--final" in sys.argv)
    print(f"== CHECAGEM DE RITMO E FIDELIDADE: {Path(pasta).name} ==")
    for i in infos:
        print("  •", i)
    for a in avisos:
        print("  ⚠ AVISO:", a)
    for e in erros:
        print("  ✗ ERRO:", e)
    if erros:
        print(f"== REPROVADO ({len(erros)} erro(s)). Corrija o gerar_edit.py/cenas e rode de novo. ==")
        return 2
    print("== APROVADO ==")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
