"""medico_render.py — Médico do render (varre o vídeo pronto atrás de defeito e conserta).

Feito do zero pro painel (nada do Auto B-Roll Studio). Reimplementa a IDEIA de um "render doctor":
depois que o vídeo é renderizado, varre o final.mp4 atrás de TELA PRETA (>= 0.3 s) e FRAME CONGELADO
(>= 0.5 s), descobre a CAUSA de cada defeito cruzando com o edit.json, explica em português e
— no modo --corrigir — arruma o que dá pra arrumar sozinho (clipe que acabou e congelou → desacelera
pra encher a cena; sobra preta no fim → encurta a duração) e manda renderizar de novo uma vez.

O painel renderiza a composição INTEIRA de uma vez (não em partes como o do David), então "re-renderizar
só a parte ruim" aqui vira: arrumar o edit.json no ponto certo e refazer o render (que já tem repetição
automática quando o Chrome cai). Defeito de "foto parada de propósito" ou "fade abrindo do preto" é
design e é ignorado.

Uso:
  python medico_render.py <pasta_projeto>              # só diagnostica e escreve medico.md
  python medico_render.py <pasta_projeto> --corrigir   # conserta o que dá + re-renderiza + confere de novo
  python medico_render.py <pasta_projeto> --json        # imprime o diagnóstico em JSON (pro servidor)

Também dá pra usar como biblioteca: diagnosticar(proj) -> dict; corrigir(proj) -> dict.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PRETO_MIN = 0.30        # tela preta a partir de 0.3 s conta como defeito (flash de corte é menor)
PRETO_PIX = 0.10        # limiar de "quão preto" (0-1); frames de corte de fonte passam disso
CONGELADO_MIN = 0.50    # frame parado a partir de 0.5 s conta
FADE_DESIGN = 1.00      # fade abrindo do preto nos primeiros 1 s de uma cena é design, ignora
VEL_MIN = 0.5           # não desacelera um clipe abaixo disso (ficaria arrastado demais)

NOFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", creationflags=NOFLAGS)


def dur_arquivo(path: Path):
    """Duração em segundos de um arquivo de mídia (ffprobe), ou None."""
    try:
        r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                  "-of", "csv=p=0", str(path)])
        return float(r.stdout.strip())
    except Exception:
        return None


def achar_video(proj: Path):
    """Acha o vídeo final igual ao servidor: final.mp4 primeiro, senão o .mp4 nomeado mais novo
    (ignora render_mudo/silent/leve/render/base). Assim funciona pros vídeos da fábrica também."""
    proj = Path(proj)
    if (proj / "final.mp4").exists():
        return proj / "final.mp4"
    vids = [f for f in proj.glob("*.mp4") if f.stem.lower() not in ("render_mudo", "silent", "leve", "render", "base")]
    return max(vids, key=lambda f: f.stat().st_mtime) if vids else None


def varrer_defeitos(video: Path):
    """Roda blackdetect + freezedetect no vídeo e devolve as duas listas de intervalos."""
    r = _run(["ffmpeg", "-v", "info", "-i", str(video), "-an",
              "-vf", f"blackdetect=d={PRETO_MIN}:pix_th={PRETO_PIX},freezedetect=n=-60dB:d={CONGELADO_MIN}",
              "-f", "null", "-"])
    log = (r.stderr or "") + (r.stdout or "")
    pretos = []
    for m in re.finditer(r"black_start:([\d.]+)\s+black_end:([\d.]+)", log):
        a, b = float(m.group(1)), float(m.group(2))
        pretos.append({"inicio": a, "fim": b, "dur": round(b - a, 2)})
    congelados, ini = [], None
    for ln in log.splitlines():
        m = re.search(r"freeze_start:\s*([\d.]+)", ln)
        if m:
            ini = float(m.group(1))
        m = re.search(r"freeze_end:\s*([\d.]+)", ln)
        if m and ini is not None:
            congelados.append({"inicio": ini, "fim": float(m.group(1)), "dur": round(float(m.group(1)) - ini, 2)})
            ini = None
    if ini is not None:   # congelou até o fim do vídeo (o ffmpeg não imprime freeze_end nesse caso)
        fim = dur_arquivo(video) or ini
        congelados.append({"inicio": ini, "fim": fim, "dur": round(fim - ini, 2)})
    return pretos, congelados


def _itens_desenham(edit):
    """Itens que pintam pixel na tela (não contam texto/legenda/param), com start/dur/src."""
    desenha = {"image", "video", "scene", "bloco", "html"}
    out = []
    for it in edit.get("items", []):
        if it.get("type") not in desenha or it.get("hidden") or it.get("by") == "template":
            continue
        p = it.get("props", {})
        s = float(it.get("start") or 0)
        d = max(0.04, float(it.get("dur") or 1))
        out.append({"it": it, "id": it.get("id"), "tipo": it["type"], "props": p,
                    "inicio": s, "fim": s + d, "dur": d, "src": p.get("src"),
                    "trim": float(p.get("trim") or 0), "speed": float(p.get("speed") or 1) or 1})
    return out


def _cobre(itens, a, b):
    """Itens que desenham e cruzam o intervalo [a,b]."""
    return [x for x in itens if x["fim"] > a + 0.01 and x["inicio"] < b - 0.01]


def diagnosticar(proj, video=None):
    """Varre o vídeo final e classifica cada defeito. Devolve dict com lista 'problemas'.
    video: caminho do vídeo a conferir (o servidor passa o find_video dele); sem isso, acha sozinho."""
    proj = Path(proj)
    video = Path(video) if video else achar_video(proj)
    if not video or not video.exists():
        return {"ok": False, "erro": "Não achei o vídeo pronto (renderize primeiro).", "problemas": []}
    try:
        edit = json.loads((proj / "edit.json").read_text(encoding="utf-8-sig"))
    except Exception:
        edit = {}
    dur_total = float(edit.get("duration") or 0) or (dur_arquivo(video) or 0)
    itens = _itens_desenham(edit)
    caiu = (proj / "render-erro.log").exists()
    pretos, congelados = varrer_defeitos(video)
    problemas = []

    for g in pretos:
        cob = _cobre(itens, g["inicio"], g["fim"])
        # fade abrindo do preto no comecinho de uma cena = design
        if any(abs(x["inicio"] - g["inicio"]) < 0.05 and g["dur"] <= FADE_DESIGN for x in cob):
            continue
        if dur_total and g["fim"] >= dur_total - 0.05 and not cob:
            problemas.append({"tipo": "preto", "inicio": g["inicio"], "fim": g["fim"], "dur": g["dur"],
                              "causa": "sobra_fim", "corrigivel": True, "item": None,
                              "texto": f"Sobra de tela preta no fim ({g['dur']}s). Dá pra encurtar a duração do vídeo."})
        elif not cob:
            problemas.append({"tipo": "preto", "inicio": g["inicio"], "fim": g["fim"], "dur": g["dur"],
                              "causa": "buraco", "corrigivel": False, "item": None,
                              "texto": f"Tela preta de {g['inicio']:.1f}s a {g['fim']:.1f}s ({g['dur']}s): não tem nenhuma cena cobrindo esse trecho (buraco na linha do tempo)."})
        else:
            alvo = cob[0]
            problemas.append({"tipo": "preto", "inicio": g["inicio"], "fim": g["fim"], "dur": g["dur"],
                              "causa": "clipe_preto" if alvo["tipo"] == "video" else "render",
                              "corrigivel": False, "item": alvo["id"],
                              "texto": f"Tela preta de {g['inicio']:.1f}s a {g['fim']:.1f}s em cima da cena “{alvo['id']}” — "
                                       + ("o clipe tem um corte preto dentro dele (troque o trecho/clipe)." if alvo["tipo"] == "video"
                                          else "o render pode ter perdido quadros aqui.")})

    for g in congelados:
        cob = _cobre(itens, g["inicio"], g["fim"])
        videos = [x for x in cob if x["tipo"] == "video"]
        if not videos:
            # foto/cena parada = design, ignora
            continue
        alvo = videos[0]
        src = alvo["src"] and (Path(alvo["src"]) if Path(alvo["src"]).is_absolute() else proj / alvo["src"])
        srcdur = dur_arquivo(src) if src and src.exists() else None
        resto = (srcdur - alvo["trim"]) if srcdur is not None else None   # quanto de clipe sobra depois do trim
        precisa = alvo["dur"] * alvo["speed"]                              # quanto de clipe a cena consome
        if resto is not None and resto < precisa - 0.05:
            problemas.append({"tipo": "congelado", "inicio": g["inicio"], "fim": g["fim"], "dur": g["dur"],
                              "causa": "clipe_curto", "corrigivel": True, "item": alvo["id"],
                              "resto": round(resto, 3), "slot": round(alvo["dur"], 3),
                              "texto": f"Frame congelado de {g['inicio']:.1f}s a {g['fim']:.1f}s na cena “{alvo['id']}”: o clipe só tem "
                                       f"{resto:.1f}s e a cena dura {alvo['dur']:.1f}s, então ele travou no último quadro. Dá pra desacelerar o clipe pra encher."})
        else:
            problemas.append({"tipo": "congelado", "inicio": g["inicio"], "fim": g["fim"], "dur": g["dur"],
                              "causa": "render", "corrigivel": False, "item": alvo["id"],
                              "texto": f"Frame congelado de {g['inicio']:.1f}s a {g['fim']:.1f}s na cena “{alvo['id']}” — o render pode ter perdido quadros."})

    return {"ok": True, "video": str(video), "duracao": round(dur_total, 2),
            "render_caiu": caiu, "pretos": len(pretos), "congelados": len(congelados),
            "problemas": problemas, "corrigiveis": sum(1 for p in problemas if p["corrigivel"])}


def _relatorio(diag):
    L = ["# Médico do render\n"]
    if not diag.get("ok"):
        return "\n".join(L + [diag.get("erro", "erro")])
    ps = diag["problemas"]
    if not ps:
        L.append("✅ Nenhum defeito encontrado — sem tela preta nem frame congelado acima do limite.")
        return "\n".join(L)
    L.append(f"Achei **{len(ps)}** ponto(s) pra olhar ({diag['corrigiveis']} dá pra consertar sozinho):\n")
    for i, p in enumerate(ps, 1):
        marca = "🔧" if p["corrigivel"] else "⚠️"
        L.append(f"{i}. {marca} {p['texto']}")
    if diag.get("render_caiu"):
        L.append("\n> Obs.: o render caiu e se recuperou nesta geração (render-erro.log). Se houver quadro perdido, renderizar de novo costuma resolver.")
    return "\n".join(L)


def corrigir(proj, render=True):
    """Aplica os consertos automáticos no edit.json e (por padrão) re-renderiza e confere de novo."""
    proj = Path(proj)
    diag = diagnosticar(proj)
    if not diag.get("ok"):
        return diag
    editp = proj / "edit.json"
    edit = json.loads(editp.read_text(encoding="utf-8-sig"))
    porid = {it.get("id"): it for it in edit.get("items", [])}
    mudou, feitos = False, []

    for p in diag["problemas"]:
        if not p["corrigivel"]:
            continue
        if p["causa"] == "clipe_curto":
            it = porid.get(p["item"])
            if not it:
                continue
            resto, slot = p["resto"], p["slot"]
            vel = max(VEL_MIN, round(resto / slot, 3))      # <1 = mais lento, estica o clipe
            it.setdefault("props", {})["speed"] = vel
            mudou = True
            feitos.append(f"Cena “{p['item']}”: clipe desacelerado pra {vel:.2f}× pra encher os {slot:.1f}s (tinha só {resto:.1f}s)."
                          + (" (no limite — pode ficar lento; melhor trocar o clipe)" if vel <= VEL_MIN else ""))
        elif p["causa"] == "sobra_fim":
            nova = round(p["inicio"], 2)
            if nova > 0.1 and nova < float(edit.get("duration") or 0):
                edit["duration"] = nova
                mudou = True
                feitos.append(f"Duração do vídeo encurtada pra {nova:.1f}s (cortou a sobra preta no fim).")

    if mudou:
        try:
            bak = editp.with_suffix(".json.bak-medico")
            if not bak.exists():
                bak.write_text(editp.read_text(encoding="utf-8-sig"), encoding="utf-8")
        except Exception:
            pass
        editp.write_text(json.dumps(edit, ensure_ascii=False, indent=2), encoding="utf-8")

    res = {"ok": True, "consertos": feitos, "mudou": mudou, "antes": diag}
    if mudou and render:
        import build_from_edit as B
        B.render(proj)
        res["depois"] = diagnosticar(proj)
    (proj / "medico.md").write_text(
        _relatorio(res.get("depois") or diag)
        + ("\n\n## Consertos aplicados\n" + "\n".join(f"- {c}" for c in feitos) if feitos else ""),
        encoding="utf-8")
    return res


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # console do Windows (cp1252) engasga nos emojis
    except Exception:
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    proj = Path(args[0])
    if "--corrigir" in sys.argv:
        res = corrigir(proj)
        if "--json" in sys.argv:
            print(json.dumps(res, ensure_ascii=False))
        else:
            for c in res.get("consertos", []):
                print("🔧", c)
            if not res.get("mudou"):
                print("Nada pra consertar sozinho.")
            d = res.get("depois") or res.get("antes")
            print("\n" + _relatorio(d))
        return
    diag = diagnosticar(proj)
    (proj / "medico.md").write_text(_relatorio(diag), encoding="utf-8")
    if "--json" in sys.argv:
        print(json.dumps(diag, ensure_ascii=False))
    else:
        print(_relatorio(diag))


if __name__ == "__main__":
    main()
