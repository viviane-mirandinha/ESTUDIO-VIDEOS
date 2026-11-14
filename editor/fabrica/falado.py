# falado.py — ferramenta "Editor de vídeo falado" do Estúdio (gravação de pessoa falando → editado). Escrito do zero.
# 100% local, zero token Claude: ffmpeg (normaliza + acha silêncios com limiar automático) → faster-whisper (palavras)
# → tira silêncios longos (respiros curtos ficam) e retakes (frase repetida logo depois) → legenda → b-roll opcional
# (Ollama escolhe os momentos, fotos grátis do Wikimedia/Pexels/Pixabay) → edit.json com CADA trecho como clipe
# (dá pra ajustar no editor) → build_from_edit --render. Saída 16:9, 9:16 ou as duas.
#
#   python falado.py --pasta <projeto>     (lê <projeto>\pedido.json)
import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ajustes, bancos, fala, ollama, relevancia  # noqa: E402
from lib.transcrever import transcrever  # noqa: E402
from lib.util import BUILD, ler_json, log, run, salvar_json  # noqa: E402

AMARELO = "#ffd400"
FONTES_PC = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
FONTE = "burbank-big-condensed-black.otf"


def prog(pct, msg):
    print(f"@@{int(pct)}|{msg}", flush=True)


def _fonte(pasta: Path):
    src = FONTES_PC / FONTE
    if not src.exists():   # sem a fonte do PC: Anton (Google Fonts, OFL; condensada e pesada) que vai no pacote
        src = next((p / "recursos" / "fontes" / "Anton-Regular.ttf" for p in Path(__file__).resolve().parents
                    if (p / "recursos" / "fontes" / "Anton-Regular.ttf").is_file()), src)
    if src.exists():
        (pasta / "fonts").mkdir(exist_ok=True)
        if not (pasta / "fonts" / src.name).exists():
            shutil.copy2(src, pasta / "fonts" / src.name)
        return {"Falado": f"fonts/{src.name}"}, "Falado"
    return {}, "Impact"


def trechos_mantidos(words, dur, sils, retake_idx, fr, min_sil=0.6, folga=0.15):
    """Trechos [s, e] do vídeo bruto que ficam. Silêncio só sai se for maior que min_sil (respiro curto fica) e
    nunca corta palavra no meio; retakes saem inteiros."""
    tirar = []
    for a, b in sils:
        a2, b2 = a + folga, b - folga
        if b2 - a2 < min_sil - 2 * folga:
            continue
        if any(w["s"] < b2 - 0.05 and w["e"] > a2 + 0.05 and (w["e"] - w["s"]) < 1.5 for w in words):   # whisper diz que tem fala aqui
            continue
        tirar.append((a2, b2))
    for k in retake_idx:
        f = fr[k]
        nx = fr[k + 1]["s"] if k + 1 < len(fr) else f["e"]
        tirar.append((max(0, f["s"] - 0.05), max(f["s"], nx - 0.08)))
    if words:   # início e fim mortos
        tirar.append((0, max(0, words[0]["s"] - 0.25)))
        tirar.append((min(dur, words[-1]["e"] + 0.5), dur))
    tirar = sorted((a, b) for a, b in tirar if b - a > 0.05)
    junt = []
    for a, b in tirar:
        if junt and a <= junt[-1][1] + 0.02:
            junt[-1] = (junt[-1][0], max(junt[-1][1], b))
        else:
            junt.append((a, b))
    manter, t = [], 0.0
    for a, b in junt:
        if a - t > 0.25:
            manter.append((round(t, 3), round(a, 3)))
        t = max(t, b)
    if dur - t > 0.25:
        manter.append((round(t, 3), round(dur, 3)))
    return manter


def remapear(words, manter):
    """Tempo do bruto → tempo do editado (palavras que caem em trecho cortado somem)."""
    out, base = [], 0.0
    for a, b in manter:
        for w in words:
            c = (w["s"] + w["e"]) / 2
            if a <= c < b:
                out.append({"w": w["w"], "s": round(base + max(0, w["s"] - a), 2), "e": round(base + min(b - a, w["e"] - a), 2)})
        base += b - a
    return out


def momentos_broll(fr_novas, n, modelo, tema):
    """Ollama escolhe as frases com coisa concreta pra mostrar + busca em inglês. Sem Ollama → frases com substantivo longo."""
    cand = [f for f in fr_novas if f["s"] >= 3 and len(f["texto"].split()) >= 5]
    if not cand or n <= 0:
        return []
    lista = "\n".join(f"{k + 1}. {f['texto'][:160]}" for k, f in enumerate(cand[:40]))
    prompt = f"""A pessoa do vídeo fala as frases abaixo{(' sobre ' + tema) if tema else ''}. Escolha até {n} frases que citam algo CONCRETO e fotografável
(lugar, objeto, animal, pessoa famosa, máquina, comida, cena) que ficaria bom como imagem por cima por 3 segundos.
Para cada uma escreva uma busca de banco de imagens em inglês (1 a 4 palavras).
{lista}
Responda SOMENTE JSON: {{"escolhas": [{{"n": 1, "busca": "..."}}]}}"""
    try:
        d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.2, num_predict=400, timeout=240))
        out = []
        for e in d.get("escolhas") or []:
            try:
                k = int(e.get("n")) - 1
            except Exception:
                continue
            if 0 <= k < len(cand) and str(e.get("busca") or "").strip():
                out.append((cand[k], str(e["busca"]).strip()[:50]))
        return out[:n]
    except Exception as e:
        log(f"Ollama (b-roll) falhou: {str(e)[:120]}")
        return []


def montar_edit(pasta, src_rel, info, manter, words_rel, W, H, brolls, titulo, nome, legenda=True):
    """edit.json: 1 item de vídeo por trecho mantido (trim = onde começa no bruto), legenda e b-roll por cima."""
    fonts, F = _fonte(pasta)
    short = H > W
    items, t = [], 0.0
    for k, (a, b) in enumerate(manter):
        items.append({"id": f"t{k + 1}", "type": "video", "track": "fundo", "label": f"Trecho {k + 1}", "start": round(t, 3), "dur": round(b - a, 3),
                      "in": "none", "out": "none", "props": {"src": src_rel, "fill": True, "fit": "cover", "trim": round(a, 3), "volume": 1}})
        t += b - a
    dur = round(t, 3)
    for k, br in enumerate(brolls):
        items.append({"id": f"b{k + 1}", "type": "image", "track": "broll", "label": "B-roll: " + br["busca"], "start": br["s"], "dur": br["d"],
                      "in": "fade", "out": "fade", "props": {"src": br["src"], "fill": True, "fit": "cover", "motion": "zoom_in", "motion_amount": 0.1}})
    if legenda:
        items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": dur, "in": "none", "out": "none",
                      "props": {"words_file": words_rel, "per_group": 2 if short else 3, "x": W / 2, "y": 1380 if short else 630, "size": 88 if short else 56,
                                "color": "#ffffff", "dim": "#ffffff" if short else "rgba(255,255,255,.7)", "hl_color": AMARELO, "keywords": [],
                                "font": F, "weight": 900, "stroke": "#000000", "stroke_w": 7 if short else 5, "upper": True}})
    if titulo:
        items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título", "start": 0, "dur": round(min(dur, 3.5), 2) if not short else dur,
                      "in": "pop", "out": "fade" if not short else "none",
                      "props": {"text": titulo, "x": W / 2, "y": 300 if short else 110, "w": 980 if short else 1100, "size": 76 if short else 56,
                                "color": "#ffffff", "font": F, "weight": 900, "align": "center", "upper": True, "bg": "rgba(0,0,0,.6)", "pad": 16,
                                "radius": 20, "shadow": False}})
    return {"version": 1, "name": nome, "canvas": {"w": W, "h": H, "fps": 30, "bg": "#000000"}, "duration": dur, "template": "generic",
            "estilo": "Editor de vídeo falado · " + ("9:16" if short else "16:9"), "ferramenta": "Editor de vídeo falado", "fonts": fonts, "audio": {},
            "tracks": [{"id": "fundo", "name": "Trechos (cortes)"}, {"id": "broll", "name": "B-roll"}, {"id": "legenda", "name": "Legenda"},
                       {"id": "textos", "name": "Textos"}], "items": items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", required=True)
    a = ap.parse_args()
    proj = Path(a.pasta)
    ped = ler_json(proj / "pedido.json")
    aj = ajustes.ler()
    modelo = ped.get("modelo") or aj["modelo_ollama"]
    t_ini = time.time()
    minutos = {}

    # 1) normaliza a gravação (30 fps constante, keyframe a cada 0,5 s: o editor pula pra qualquer trecho) -----
    t0 = time.time()
    bruto = proj / "bruto.mp4"
    if not bruto.exists():
        prog(2, "Preparando a sua gravação…")
        src = Path(ped["arquivo"])
        info0 = fala.probe(src)
        if not info0["audio"]:
            raise SystemExit("Esse vídeo não tem som — o editor de vídeo falado precisa da sua voz.")
        vert = info0["h"] > info0["w"]
        vf = "fps=30," + ("scale=720:-2" if vert else "scale=-2:720")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-g", "15",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(bruto)], quiet=True)
        try:
            src.unlink()   # era a cópia enviada pelo painel (fica só o bruto normalizado)
        except Exception:
            pass
    info = fala.probe(bruto)
    minutos["preparar"] = round((time.time() - t0) / 60, 2)

    # 2) transcrição + silêncios ---------------------------------------------------------
    t0 = time.time()
    wav = proj / "audio.wav"
    fala.extrair_audio(bruto, wav)
    if not (proj / "words_bruto.json").exists():
        prog(10, f"Transcrevendo {int(info['dur'] // 60)} min {int(info['dur'] % 60)} s de fala (Whisper)…")
        idioma = ped.get("idioma") or aj["idioma"]
        transcrever(wav, proj / "words_bruto.json", idioma=fala.WHISPER_LANG.get(idioma, "pt"))
    words = ler_json(proj / "words_bruto.json")
    prog(40, "Achando os silêncios e as repetições…")
    sils, lim = fala.silencios(wav, 0.35) if ped.get("silencio", True) else ([], None)
    fr = fala.frases(words)
    rt = fala.retakes(fr) if ped.get("retakes", True) else []
    manter = trechos_mantidos(words, info["dur"], sils, rt, fr, min_sil=float(ped.get("min_sil") or 0.6))
    novo_dur = sum(b - a for a, b in manter)
    log(f"silêncios: {len(sils)} (limiar {lim} dB) · retakes: {len(rt)} · {len(manter)} trechos · {info['dur']:.1f}s → {novo_dur:.1f}s")
    words_novas = remapear(words, manter)
    salvar_json(proj / "words.json", words_novas)
    salvar_json(proj / "cortes.json", {"manter": manter, "silencios": sils, "limiar_db": lim, "retakes": [fr[k]["texto"] for k in rt],
                                       "duracao_original": round(info["dur"], 2), "duracao_editada": round(novo_dur, 2)})
    minutos["transcrever_cortar"] = round((time.time() - t0) / 60, 2)

    # 3) b-roll (opcional) ---------------------------------------------------------------
    t0 = time.time()
    brolls_base = []
    if ped.get("broll"):
        prog(46, "Escolhendo onde entra b-roll (IA local)…")
        frn = fala.frases(words_novas)
        n = max(1, min(12, int(ped.get("n_broll") or max(1, novo_dur // 12))))
        escolhas = momentos_broll(frn, n, modelo, ped.get("titulo") or "")
        chaves = {"pexels": aj.get("pexels_key"), "pixabay": aj.get("pixabay_key")}
        usados, ultimo = set(), -99
        for k, (f, q) in enumerate(sorted(escolhas, key=lambda x: x[0]["s"])):
            if f["s"] - ultimo < 7:   # máx. 1 b-roll a cada ~7 s (a pessoa continua aparecendo)
                continue
            prog(48 + 10 * k / max(1, len(escolhas)), f"Buscando b-roll: {q}…")
            cands = bancos.candidatos(q, chaves)
            esc = bancos.melhor([c for c in cands if c["tipo"] == "image"], usados, query=q, ents=relevancia.entidades(f["texto"]))
            if not esc:
                continue
            try:
                srcb = bancos.baixar(esc, proj, 100 + k)
            except Exception as e:
                log(f"b-roll '{q}' falhou: {str(e)[:80]}")
                continue
            usados.add(esc["url"])
            d = round(min(3.2, max(2.0, f["e"] - f["s"])), 2)
            brolls_base.append({"s": round(f["s"], 2), "d": d, "src": srcb, "busca": q, "texto": f["texto"][:80], "fonte": esc.get("fonte"),
                                "licenca": esc.get("licenca"), "pagina": esc.get("pagina")})
            ultimo = f["s"]
        salvar_json(proj / "img" / "creditos.json" if (proj / "img").exists() else proj / "creditos_broll.json", brolls_base)
    minutos["broll"] = round((time.time() - t0) / 60, 2)

    # 4) edit.json + render (16:9, 9:16 ou os dois) -----------------------------------------
    t0 = time.time()
    saida = ped.get("saida") or "16:9"
    titulo = (ped.get("titulo") or "").strip()
    nn = proj.name[:2] if proj.name[:2].isdigit() else "00"
    base_nome = f"{nn} - {datetime.now().strftime('%d-%m-%Y')} - {titulo or 'Vídeo falado'}"
    feitos = []
    vert_src = info["h"] > info["w"]
    alvos = []
    if saida in ("16:9", "ambos") and not vert_src:
        alvos.append(("16:9", proj, "bruto.mp4", "words.json"))
    if saida in ("9:16", "ambos") or vert_src:
        alvos.append(("9:16", proj / "vertical" if alvos else proj, "../bruto.mp4" if alvos else "bruto.mp4", "../words.json" if alvos else "words.json"))
    for k, (fmt, pasta, src_rel, w_rel) in enumerate(alvos):
        pasta.mkdir(exist_ok=True)
        W, H = (1280, 720) if fmt == "16:9" else (1080, 1920)
        brs = [{**b, "src": ("../" + b["src"]) if pasta != proj else b["src"]} for b in brolls_base]
        if pasta != proj:   # o editor só lê mídia DENTRO da pasta do projeto → hardlink do bruto e das palavras
            for f in ("bruto.mp4", "words.json"):
                dst = pasta / f
                if dst.exists():
                    dst.unlink()
                try:
                    import os
                    os.link(proj / f, dst)
                except OSError:
                    shutil.copy2(proj / f, dst)
            src_rel, w_rel = "bruto.mp4", "words.json"
            if brolls_base:
                (pasta / "img").mkdir(exist_ok=True)
                for b in brolls_base:
                    shutil.copy2(proj / b["src"], pasta / b["src"])
                brs = brolls_base
        nome = base_nome + (" (vertical)" if fmt == "9:16" else "")
        ed = montar_edit(pasta, src_rel, info, manter, w_rel, W, H, brs, titulo, nome, legenda=ped.get("legenda", True))
        salvar_json(pasta / "edit.json", ed)
        prog(60 + 38 * k / len(alvos), f"Renderizando o vídeo {fmt} ({len(manter)} trechos)…")
        run([sys.executable, BUILD, str(pasta), "--render"], timeout=7200)
        feitos.append({"formato": fmt, "pasta": str(pasta), "rendered": (pasta / "final.mp4").exists()})
    minutos["montar_render"] = round((time.time() - t0) / 60, 2)
    wav.unlink(missing_ok=True)
    rel = {"ferramenta": "Editor de vídeo falado", "estilo": "Editor de vídeo falado", "titulo": titulo or proj.name,
           "inicio": datetime.fromtimestamp(t_ini).astimezone().isoformat(timespec="seconds"), "fim": datetime.now().astimezone().isoformat(timespec="seconds"),
           "minutos": round((time.time() - t_ini) / 60, 2), "minutos_por_etapa": minutos, "duracao_original": round(info["dur"], 1),
           "duracao_video": round(novo_dur, 1), "trechos": len(manter), "silencios_tirados": max(0, len(manter) - 1 - len(rt)), "silencios_detectados": len(sils), "retakes_tirados": len(rt),
           "brolls": len(brolls_base), "saidas": feitos, "tokens": 0, "custo_usd": 0,
           "observacoes": f"EDITOR DE VÍDEO FALADO (zero token Claude): {info['dur']:.0f}s → {novo_dur:.0f}s; silêncio limiar {lim} dB (auto), "
                          f"{len(rt)} retakes; {len(brolls_base)} b-roll; saída {saida}"}
    salvar_json(proj / "RELATORIO.json", rel)
    for f in feitos:
        if Path(f["pasta"]) != proj:
            salvar_json(Path(f["pasta"]) / "RELATORIO.json", rel)
    prog(100, "Pronto!")
    print("FALADO PRONTO", flush=True)


if __name__ == "__main__":
    main()
