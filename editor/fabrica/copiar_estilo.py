# copiar_estilo.py — "🎨 Copiar estilo de edição — modo rápido (aproximado, grátis)". Escrito do zero pro Estúdio.
# Mede a referência com ferramentas locais (yt-dlp + ffmpeg + numpy/PIL + faster-whisper) e salva um ESTILO APROXIMADO
# (preset do Vídeo com imagens / Fábrica de Shorts): ritmo de corte, cores, posição e tamanho da legenda, fonte, zoom.
# Não copia nada da referência (nem imagem, nem logo, nem texto): só números. Zero token Claude.
#
#   python copiar_estilo.py --pasta <trabalho>     (lê <trabalho>\pedido.json: {url | arquivo, nome})
import argparse
import colorsys
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import elementos as ELEM, fala, preencher_preset, rede_yt  # noqa: E402
from lib.transcrever import transcrever  # noqa: E402
from lib.util import ESTILOS, ler_json, log, run, salvar_json, slug  # noqa: E402

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def prog(pct, msg):
    print(f"@@{int(pct)}|{msg}", flush=True)


def cortes_de_cena(video, dur):
    """Tempos dos cortes E das transições suaves (fade/dissolve/motion graphics).
    Lê o vídeo a 4 quadros/s em miniatura e mede quanto cada quadro muda do anterior (histograma + imagem grossa).
    O limite é adaptativo (mediana + 4×desvio), então câmera mexendo não vira corte e transição suave não some."""
    fps, W, H = 4, 32, 18
    r = subprocess.run(["ffmpeg", "-v", "error", "-t", f"{dur:.2f}", "-i", str(video), "-an", "-vf", f"fps={fps},scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, creationflags=NOWIN)
    n = len(r.stdout) // (W * H)
    if n < 3:
        return []
    f = np.frombuffer(r.stdout[: n * W * H], dtype=np.uint8).reshape(n, H, W).astype(np.float32)
    hist = np.stack([np.histogram(x, bins=24, range=(0, 256))[0] for x in f]).astype(np.float32) / (W * H)
    d_hist = np.abs(np.diff(hist, axis=0)).sum(axis=1) / 2           # 0..1
    d_pix = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2)) / 255        # 0..1
    sc = 0.6 * d_hist + 0.4 * np.minimum(1.0, d_pix * 2.5)
    med = float(np.median(sc))
    mad = float(np.median(np.abs(sc - med))) or 0.005
    thr = max(0.12, med + 4 * mad)
    picos = [i for i in range(len(sc)) if sc[i] >= thr and sc[i] >= sc[max(0, i - 1)] and sc[i] >= sc[min(len(sc) - 1, i + 1)]]
    out = []
    for i in picos:   # junta picos colados (flash, vinheta, transição de 2 quadros) num corte só
        t = (i + 1) / fps
        if not out or t - out[-1] >= 0.75:
            out.append(t)
    return out


def quadros(video, dur, n, pasta):
    pasta.mkdir(exist_ok=True)
    out = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        f = pasta / f"q{k:02d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=480:-2,format=yuvj420p", str(f)],
                       capture_output=True, creationflags=NOWIN)
        if f.exists():
            out.append(f)
    return out


def paleta(imgs, k=6):
    """Cores dominantes (quantização) + destaque = a mais saturada e clara entre as frequentes."""
    px = []
    for f in imgs:
        im = Image.open(f).convert("RGB").resize((96, 54))
        px.append(np.asarray(im).reshape(-1, 3))
    a = np.concatenate(px).astype(np.uint8)
    im = Image.fromarray(a.reshape(1, -1, 3)).quantize(colors=12, method=Image.Quantize.MEDIANCUT)
    pal = im.getpalette()[:36]
    cont = sorted(im.getcolors(), key=lambda x: -x[0])
    total = sum(c for c, _ in cont)
    cores = []
    for c, idx in cont:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        cores.append({"hex": f"#{r:02x}{g:02x}{b:02x}", "pct": round(100 * c / total, 1), "sat": round(s, 2), "luz": round(l, 2)})
    vivas = [c for c in cores if c["sat"] >= 0.45 and 0.35 <= c["luz"] <= 0.75 and c["pct"] >= 1]
    destaque = max(vivas, key=lambda c: c["sat"] * c["pct"] ** 0.3)["hex"] if vivas else None   # None = o vídeo não tem cor viva
    escura = min(cores, key=lambda c: c["luz"])["hex"] if cores else "#05060a"
    return cores[:k], destaque, escura


def faixas_texto(imgs):
    """Texto/legenda na tela, por contagem simples: em cada quadro, divide a altura em 10 faixas e mede bordas fortes
    finas (letras) + pixels quase brancos/amarelos. Faixa com muito disso em vários quadros = tem texto ali."""
    marcas = np.zeros(10)
    por_quadro = []
    for f in imgs:
        im = Image.open(f).convert("L")
        w, h = im.size
        ed = np.asarray(im.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
        rgb = np.asarray(Image.open(f).convert("RGB"), dtype=np.int16)
        claro = ((rgb.min(axis=2) > 215) | ((rgb[..., 0] > 200) & (rgb[..., 1] > 180) & (rgb[..., 2] < 90))).astype(np.float32)
        tem = []
        x0, x1 = int(w * 0.12), int(w * 0.88)   # legenda fica no meio; as bordas da tela só atrapalham a conta
        for b in range(10):
            y0, y1 = int(h * b / 10), int(h * (b + 1) / 10)
            faixa_ed, faixa_cl = ed[y0:y1, x0:x1] > 70, claro[y0:y1, x0:x1]
            dens = float(faixa_ed.mean())
            cl = float(faixa_cl.mean())
            # letras: muita borda fina + um pouco de branco/amarelo, concentrados num pedaço da linha (texto não ocupa a largura toda)
            col = faixa_cl.mean(axis=0)
            junto = float((col > 0.04).mean())
            tem.append(dens > 0.045 and 0.006 < cl < 0.35 and 0.08 < junto < 0.95)
        por_quadro.append(tem)
        marcas += np.array(tem, dtype=np.float32)
    frac = marcas / max(1, len(imgs))
    return frac, por_quadro


def duracao_link(url):
    try:
        r = subprocess.run([*rede_yt.cmd(), "--no-warnings", "--no-playlist", "--skip-download", "--print", "duration", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        return float(r.stdout.strip().splitlines()[-1])
    except Exception:
        return 0.0


def analisar(video, pasta: Path, dur_total=0.0):
    info = fala.probe(video)
    dur = min(info["dur"], 180.0)
    prog(25, "Contando os cortes (ritmo da edição)…")
    cs = [t for t in cortes_de_cena(video, dur) if 0.5 < t <= dur - 0.3]
    cortes_min = round(len(cs) / (dur / 60), 1) if dur else 0
    plano_medio = round(dur / (len(cs) + 1), 2) if dur else 0   # média coerente com cortes/min (a mediana distorcia com vinheta/flash)
    prog(45, "Lendo cores e textos dos quadros…")
    imgs = quadros(video, dur, 16, pasta / "_quadros")
    cores, destaque, escura = paleta(imgs)
    frac, _ = faixas_texto(imgs)
    baixo, meio, topo = float(frac[6:9].max()), float(frac[3:7].max()), float(frac[0:3].max())
    tem_legenda = max(baixo, meio) >= 0.3
    pos = "baixo" if baixo >= meio and baixo >= 0.3 else ("centro" if meio >= 0.3 else "baixo")
    texto_tela = round(100 * float(frac.mean()), 1)
    prog(60, "Ouvindo se tem narração (Whisper, 60 s)…")
    tem_narr, ppm = False, 0
    if info["audio"]:
        wav = pasta / "_amostra.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-t", "60", "-vn", "-ac", "1", "-ar", "16000", str(wav)], quiet=True)
        try:
            transcrever(wav, pasta / "_words.json", idioma="auto")
            ws = ler_json(pasta / "_words.json")
            ppm = int(len(ws) / (min(60, dur) / 60))
            tem_narr = ppm >= 70
        except Exception as e:
            log(f"whisper falhou: {str(e)[:120]}")
        wav.unlink(missing_ok=True)
    # contact sheet (fica só local, vira a capa do estilo)
    if imgs:
        thumbs = [Image.open(f).convert("RGB").resize((240, int(240 * Image.open(f).size[1] / Image.open(f).size[0]))) for f in imgs[:8]]
        tw, th = thumbs[0].size
        sheet = Image.new("RGB", (tw * 4, th * 2), "#000")
        for k, t in enumerate(thumbs):
            sheet.paste(t, ((k % 4) * tw, (k // 4) * th))
        sheet.save(pasta / "capa.jpg", quality=85)
    if imgs:
        shutil.copy2(imgs[len(imgs) // 2], pasta / "_fundo.jpg")   # fundo da prévia (só local, apagado no fim)
    shutil.rmtree(pasta / "_quadros", ignore_errors=True)
    formato = "short" if info["h"] > info["w"] else "longo"
    prog(75, "Procurando as peças gráficas (título, etiquetas, números, créditos)…")
    try:
        pecas, ocr_ok = ELEM.detectar(video, dur, pasta / "_pecas", vertical=formato == "short", prog=lambda f: prog(75 + 12 * f, "Procurando as peças gráficas…"))
    except Exception as e:
        log(f"peças: falhou ({str(e)[:120]})")
        pecas, ocr_ok = [], False
    shutil.rmtree(pasta / "_pecas", ignore_errors=True)
    return {"formato": formato, "w": info["w"], "h": info["h"], "duracao_analisada": round(dur, 1),
            "cortes": len(cs), "cortes_por_min": cortes_min, "plano_medio_s": plano_medio, "cores": cores, "cor_destaque": destaque, "cor_escura": escura,
            "pecas": pecas, "pecas_ocr": ocr_ok,
            "texto_na_tela_pct": texto_tela, "tem_legenda": tem_legenda, "legenda_pos": pos, "tem_narracao": tem_narr, "palavras_por_min": ppm,
            "avisos": avisos_referencia(formato, dur_total or info["dur"], cortes_min, texto_tela, tem_narr, info["audio"])}


def avisos_referencia(formato, dur_total, cortes_min, texto_tela, tem_narr, tem_audio):
    """Referência ruim gera estilo genérico: avisa o que atrapalha (boa ref = 8-25 min, muito grafismo, um estilo só)."""
    av = []
    if cortes_min < 4:
        av.append("Esse vídeo quase não troca de cena (parece alguém falando pra câmera). O estilo vai sair parado — escolha um vídeo com mais cortes.")
    if texto_tela < 3:
        av.append("Quase não tem texto ou desenho na tela — o estilo vai copiar só as cores e o ritmo.")
    if tem_audio and not tem_narr:
        av.append("Não ouvi uma narração do começo ao fim — usei a velocidade de fala normal.")
    if formato == "longo" and dur_total and not 8 * 60 <= dur_total <= 25 * 60:
        av.append(f"Esse vídeo tem {dur_total / 60:.0f} min. Funciona melhor com um de 8 a 25 min que tenha o mesmo jeito do começo ao fim.")
    return av


def _preset_pecas(an):
    """Ajustes do preset que vêm das peças achadas (legenda em caixa, transição) + a lista de peças."""
    pecas = an.get("pecas") or []
    out = {"elementos": pecas}
    lg = ELEM.por_tipo(pecas, "legenda")
    if lg:
        out["legenda_caixa"] = bool(lg.get("caixa"))
        y = lg.get("y") or 0.85
        out["legenda_pos"] = "topo" if y < 0.33 else ("centro" if y < 0.68 else "baixo")
    tr = ELEM.por_tipo(pecas, "transicao")
    if tr:
        out.update({"flash": {"flash_cada": 3}, "seco": {"transicao": 0.0, "flash_cada": 0}, "suave": {"transicao": 0.5, "flash_cada": 0}}[tr["modo"]])
    return out


def preset_de(an):
    short = an["formato"] == "short"
    pm = max(1.2, min(8.0, an["plano_medio_s"] or 4))
    rapido = an["cortes_por_min"] >= 18
    return {"formato": an["formato"], "cor_destaque": an["cor_destaque"] or "#ffd400", "destaque_padrao": not an["cor_destaque"], "fundo": an["cor_escura"], "fonte": "condensada",
            "legenda": bool(an["tem_legenda"] or short), "legenda_pos": "centro" if short and an["legenda_pos"] != "baixo" else an["legenda_pos"],
            "legenda_palavras": 2 if (short or rapido) else 3, "titulo_fixo": short, "zoom": 0.18 if rapido else 0.12,
            "flash_cada": 3 if rapido else (5 if pm < 4 else 0), "vinheta": True, "cartao_final": True, "cta": not short,
            "transicao": 0.15 if rapido else 0.4, **_preset_pecas(an)}, round(max(1.0, pm * 0.7), 2), round(max(1.8, pm * 1.35), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", required=True)
    a = ap.parse_args()
    pasta = Path(a.pasta)
    ped = ler_json(pasta / "pedido.json")
    t0 = time.time()
    ref = pasta / "ref.mp4"
    if not ref.exists():
        if ped.get("url"):
            prog(3, "Baixando os primeiros 3 minutos da referência…")
            fala.baixar_link(ped["url"], ref, "*0-180")
        else:
            shutil.move(ped["arquivo"], ref)
    an = analisar(ref, pasta, duracao_link(ped["url"]) if ped.get("url") else 0.0)
    preset, smin, smax = preset_de(an)
    nome = (ped.get("nome") or "").strip() or f"Meu estilo {datetime.now().strftime('%d-%m %H%M')}"
    eid = "meu-" + (slug(nome, 30) or "estilo")
    prog(90, "Salvando o estilo aproximado…")
    from lib.texto import descricao_estilo_copiado
    desc = descricao_estilo_copiado(an)   # 07/11: frase simples (os números técnicos ficam em "analise")
    cfg = {"nome": nome, "nome_curto": nome, "descricao": desc, "imagens": "wikimedia", "clipes": True, "vertical": an["formato"] == "short",
           "so_ferramenta": True, "aproximado": True, "formato": an["formato"], "dica_busca": "real photographs and stock footage",
           "extra_busca": "", "preferir_titulo": ["photo", "photograph"], "shot_min": smin, "shot_max": smax,
           "palavras_por_minuto": max(130, min(190, an["palavras_por_min"] or 155)), "pad_fim": 0.6 if an["formato"] == "short" else 2.4,
           "roteiro_prompt": "vídeo narrado, fatos reais", "copiar": [], "preset": preset, "analise": an,
           "referencia": {"video": ped.get("url") or "", "titulo": ped.get("titulo") or ""}, "criado": datetime.now().isoformat(timespec="seconds")}
    dst = ESTILOS / eid
    preencher_preset.criar_estilo(dst, cfg)
    if (pasta / "capa.jpg").exists():
        shutil.copy2(pasta / "capa.jpg", dst / "capa.jpg")
    try:
        if (pasta / "_fundo.jpg").exists():   # fundo da prévia = um quadro da referência bem desfocado (só pra dar o clima)
            Image.open(pasta / "_fundo.jpg").convert("RGB").filter(ImageFilter.GaussianBlur(7)).save(dst / "previa_fundo.jpg", quality=80)
        ELEM.previa(preset.get("elementos") or [], preset, dst / "previa.jpg", dst / "previa_fundo.jpg")
    except Exception as e:
        log(f"prévia: falhou ({str(e)[:120]})")
    (pasta / "_fundo.jpg").unlink(missing_ok=True)
    res = {"estilo_id": eid, "nome": nome, "analise": an, "preset": preset, "shot_min": smin, "shot_max": smax, "descricao": desc,
           "segundos": round(time.time() - t0, 1), "tokens": 0}
    salvar_json(pasta / "resultado.json", res)
    ref.unlink(missing_ok=True)   # a referência não fica guardada (só os números)
    prog(100, "Estilo salvo!")
    print("ESTILO " + eid, flush=True)


if __name__ == "__main__":
    main()
