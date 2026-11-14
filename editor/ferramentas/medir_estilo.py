# -*- coding: utf-8 -*-
# medir_estilo.py — mede o estilo de edição de um vídeo de referência e gera a "ficha de estilo".
# Código próprio do Estúdio de Vídeos, escrito do zero (ffmpeg/ffprobe + numpy + Pillow; sem GPU).
# Não copia nada da referência (nem imagem, nem texto, nem áudio): só extrai NÚMEROS.
#
#   python medir_estilo.py ref/ref.mp4
#
# Saída (na mesma pasta do vídeo): ESTILO-MEDIDO.json, ESTILO-MEDIDO.md, sheet-medido.jpg
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def rodar(cmd, binario=False):
    r = subprocess.run(cmd, capture_output=True, creationflags=NOWIN)
    if binario:
        return r.stdout, r.stderr.decode("utf-8", "replace")
    return r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


# ---------------------------------------------------------------- informações básicas
def sondar(video):
    out, _ = rodar(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)])
    d = json.loads(out or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den or 0) else 0.0
    dur = float(d.get("format", {}).get("duration") or v.get("duration") or 0)
    return {"duracao_s": round(dur, 2), "largura": w, "altura": h, "fps": round(fps, 2), "tem_audio": a is not None}


def proporcao(w, h):
    if not w or not h:
        return "?"
    r = w / h
    for nome, val in (("16:9", 16 / 9), ("9:16", 9 / 16), ("1:1", 1.0), ("4:5", 0.8), ("4:3", 4 / 3), ("21:9", 21 / 9)):
        if abs(r - val) < 0.04:
            return nome
    return f"{r:.2f}:1"


# ---------------------------------------------------------------- cortes (ffmpeg scene)
def detectar_cortes(video, limiar=0.3):
    _, err = rodar(["ffmpeg", "-hide_banner", "-i", str(video), "-an", "-vf",
                    f"select='gt(scene,{limiar})',showinfo", "-f", "null", "-"])
    return [round(float(m), 3) for m in re.findall(r"pts_time:([0-9.]+)", err)]


def ler_quadros(video, fps, larg, cinza=False):
    """Lê quadros em miniatura direto do ffmpeg (rawvideo). Retorna array (n, h, w[, 3])."""
    canais = 1 if cinza else 3
    pix = "gray" if cinza else "rgb24"
    out, _ = rodar(["ffmpeg", "-v", "error", "-i", str(video), "-an", "-vf",
                    f"fps={fps},scale={larg}:-2:flags=area,format={pix}", "-f", "rawvideo", "-"], binario=True)
    return out


def quadros(video, info, fps, larg, cinza=False):
    w, h = info["largura"], info["altura"]
    alt = int(round(larg * h / w / 2) * 2) if w else larg
    out = ler_quadros(video, fps, larg, cinza)
    c = 1 if cinza else 3
    tam = larg * alt * c
    n = len(out) // tam
    arr = np.frombuffer(out[: n * tam], dtype=np.uint8)
    return arr.reshape((n, alt, larg) if cinza else (n, alt, larg, 3))


def tipo_transicao(rgb, fps, cortes):
    """Classifica cada corte: seco (1 salto), dissolve (mudança espalhada em vários quadros) ou fade p/ preto."""
    if len(rgb) < 3 or not cortes:
        return {"seco": 0, "dissolve": 0, "fade_preto": 0}
    luma = rgb.mean(axis=3)
    medias = luma.mean(axis=(1, 2))
    dif = np.abs(np.diff(luma, axis=0)).mean(axis=(1, 2))
    base = np.median(dif) + 1e-6
    cont = {"seco": 0, "dissolve": 0, "fade_preto": 0}
    for t in cortes:
        i = int(round(t * fps))
        a, b = max(0, i - 3), min(len(dif), i + 3)
        if b - a < 2:
            continue
        if medias[max(0, i - 3): min(len(medias), i + 3)].min() < 18:
            cont["fade_preto"] += 1
            continue
        janela = dif[a:b]
        altos = int((janela > max(base * 3, janela.max() * 0.35)).sum())
        cont["dissolve" if altos >= 3 else "seco"] += 1
    return cont


# ---------------------------------------------------------------- cor
def paleta(rgb, k=5, iters=15):
    px = rgb.reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(7)
    if len(px) > 60000:
        px = px[rng.choice(len(px), 60000, replace=False)]
    # k-means++ simples
    cent = [px[rng.integers(len(px))]]
    for _ in range(1, k):
        d = np.min(((px[:, None, :] - np.array(cent)[None]) ** 2).sum(2), axis=1)
        cent.append(px[rng.choice(len(px), p=d / d.sum())])
    cent = np.array(cent)
    for _ in range(iters):
        lab = np.argmin(((px[:, None, :] - cent[None]) ** 2).sum(2), axis=1)
        for j in range(k):
            sel = px[lab == j]
            if len(sel):
                cent[j] = sel.mean(0)
    lab = np.argmin(((px[:, None, :] - cent[None]) ** 2).sum(2), axis=1)
    pesos = np.bincount(lab, minlength=k) / len(lab)
    ordem = np.argsort(-pesos)
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in cent[j]), "peso_pct": round(float(pesos[j]) * 100, 1)}
            for j in ordem]


def saturacao_media(rgb):
    x = rgb.reshape(-1, 3).astype(np.float32)
    mx, mn = x.max(1), x.min(1)
    return float(np.mean(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)))


def cor_destaque(pal):
    """Cor mais saturada (e não quase preta) da paleta = candidata a cor de destaque."""
    melhor, nota = None, -1
    for c in pal:
        r, g, b = (int(c["hex"][i:i + 2], 16) for i in (1, 3, 5))
        mx, mn = max(r, g, b), min(r, g, b)
        s = (mx - mn) / mx if mx else 0
        if mx > 60 and s * mx > nota:
            melhor, nota = c["hex"], s * mx
    return melhor


def destaque_saturado(rgb):
    """Cor de destaque real: agrupa só os pixels bem saturados (títulos/realces), mesmo que ocupem pouca área."""
    if not len(rgb):
        return None
    x = rgb.reshape(-1, 3).astype(np.float32)
    mx, mn = x.max(1), x.min(1)
    sel = x[(mx > 90) & ((mx - mn) / np.maximum(mx, 1) > 0.55)]
    if len(sel) < 0.002 * len(x):
        return None
    grupos = [g for g in paleta(sel.reshape(-1, 1, 3).astype(np.uint8), k=4) if g["peso_pct"] >= 12]

    def viva(h):
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
        return (max(r, g, b) - min(r, g, b)) * max(r, g, b)
    return max(grupos, key=lambda g: viva(g["hex"]))["hex"] if grupos else None


# ---------------------------------------------------------------- texto na tela (heurística)
def faixas_de_texto(cinza):
    """Por quadro: procura faixa horizontal com muita borda forte (letras) — no terço central e no inferior.
    Retorna % de quadros com texto em cada região e a altura típica da faixa (≈ tamanho da letra)."""
    n, H, W = cinza.shape
    res = {"central": [], "inferior": []}
    alturas = []
    for q in cinza.astype(np.int16):
        gx = np.abs(np.diff(q, axis=1))[:-1, :]
        gy = np.abs(np.diff(q, axis=0))[:, :-1]
        borda = (gx + gy) > 90
        x0, x1 = int(W * 0.1), int(W * 0.9)
        dens = borda[:, x0:x1].mean(axis=1)
        for nome, (a, b) in (("central", (H // 3, 2 * H // 3)), ("inferior", (2 * H // 3, H - 2))):
            linhas = dens[a:b] > 0.12
            maior, atual = 0, 0
            for v in linhas:
                atual = atual + 1 if v else 0
                maior = max(maior, atual)
            tem = maior >= max(3, int(H * 0.035)) and dens[a:b].mean() > 0.04
            res[nome].append(tem)
            if tem:
                alturas.append(maior / H)
    out = {k: round(100 * float(np.mean(v)), 1) if v else 0.0 for k, v in res.items()}
    out["altura_faixa_pct_tela"] = round(100 * float(np.median(alturas)), 1) if alturas else 0.0
    return out


# ---------------------------------------------------------------- áudio
def loudness(video):
    _, err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn", "-af", "ebur128=peak=true",
                    "-f", "null", "-"])
    resumo = err[err.rfind("Summary:"):] if "Summary:" in err else err

    def pega(rot):
        m = re.search(rot + r":\s*(-?[0-9.]+|-inf)", resumo)
        return None if not m or m.group(1) == "-inf" else float(m.group(1))
    return {"integrado_lufs": pega("I"), "faixa_lra_lu": pega("LRA"), "pico_dbfs": pega("Peak")}


def ler_audio(video, sr=16000):
    out, _ = rodar(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                   binario=True)
    return np.frombuffer(out, dtype=np.float32)


def analisar_audio(x, sr=16000):
    if len(x) < sr:
        return {"tipo": "sem áudio"}
    hop, win = 160, 512  # 10 ms
    n = (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    fr = x[idx] * np.hanning(win)[None, :].astype(np.float32)
    esp = np.abs(np.fft.rfft(fr, axis=1))
    freqs = np.fft.rfftfreq(win, 1 / sr)
    energia = (esp ** 2).sum(1) + 1e-12
    db = 10 * np.log10(energia)
    # energia em blocos de 50 ms
    b = 5
    dbb = db[: len(db) // b * b].reshape(-1, b).mean(1)
    p95 = np.percentile(dbb, 95)
    pausas = float(np.mean(dbb < p95 - 25))           # quase silêncio
    p10_rel = float(np.percentile(dbb, 10) - p95)      # quão fundo o "chão" cai
    graves = esp[:, (freqs >= 30) & (freqs < 150)].sum(1)
    medios = esp[:, (freqs >= 300) & (freqs < 3400)].sum(1) + 1e-9
    agudos = esp[:, (freqs >= 5000)].sum(1)
    quietos = db < np.percentile(db, 30)               # entre palavras
    graves_quietos = float(np.median(graves[quietos] / medios[quietos])) if quietos.any() else 0.0
    if pausas < 0.06 and p10_rel > -22:
        tipo = "música contínua (trilha presente, provavelmente o tempo todo)"
        musica = True
    elif pausas > 0.18 or p10_rel < -35:
        tipo = "só voz (pausas silenciosas entre frases, sem trilha)"
        musica = False
    else:
        tipo = "voz + música baixa por baixo (incerto)"
        musica = True
    # BPM: fluxo espectral -> autocorrelação 60-180 BPM
    fluxo = np.maximum(np.diff(np.log1p(esp), axis=0), 0).sum(1)
    fluxo = fluxo - np.convolve(fluxo, np.ones(50) / 50, mode="same")
    fluxo = np.maximum(fluxo, 0)
    bpm, conf = None, 0.0
    if len(fluxo) > 1000:
        f = fluxo - fluxo.mean()
        ac = np.correlate(f[:6000], f[:6000], mode="full")[len(f[:6000]) - 1:]
        fps_env = sr / hop
        lmin, lmax = int(fps_env * 60 / 180), int(fps_env * 60 / 60)
        seg = ac[lmin:lmax]
        if seg.size and ac[0] > 0:
            lag = lmin + int(np.argmax(seg))
            conf = float(seg.max() / ac[0])
            bpm = round(60 * fps_env / lag, 1)
    return {"tipo": tipo, "tem_musica": musica, "pausas_pct": round(100 * pausas, 1),
            "chao_rel_db": round(p10_rel, 1), "graves_entre_falas": round(graves_quietos, 3),
            "agudos_rel": round(float(np.median(agudos / medios)), 3),
            "bpm_aprox": bpm if (bpm and conf > 0.12) else None, "bpm_confianca": round(conf, 2)}


# ---------------------------------------------------------------- contact-sheet
def contact_sheet(video, dur, destino, n=20):
    fps = max(n / max(dur, 1), 0.01)
    rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf",
           f"fps={fps:.4f},scale=320:-2,tile=5x4", "-frames:v", "1", "-q:v", "4", str(destino)])
    return destino.exists()


# ---------------------------------------------------------------- recomendações
def recomendar(m):
    cpm = m["cortes"]["por_minuto"]
    plano = m["cortes"]["plano_medio_s"]
    br = m["imagem"]["brilho_medio"]
    sat = m["imagem"]["saturacao_media"]
    txt = max(m["texto"]["central"], m["texto"]["inferior"])
    vertical = m["video"]["altura"] > m["video"]["largura"]
    if br > 170 and sat < 0.25:
        fonte, porque = "Patrick Hand (ou Kalam)", "fundo claro e pouco saturado — cara de quadro/whiteboard"
    elif br < 85 and cpm < 20:
        fonte, porque = "Oswald (títulos) + Inter (legenda)", "tom escuro e ritmo calmo — documental/sério"
    elif br < 85:
        fonte, porque = "Bebas Neue (títulos) + Inter (legenda)", "escuro e rápido — dark/mistério"
    elif cpm > 30 or txt > 40:
        fonte, porque = "Anton (ou Montserrat 900)", "muito texto/corte rápido — estilo retenção"
    else:
        fonte, porque = "Montserrat 800", "neutro"
    tr = m["cortes"]["transicoes"]
    tot = max(1, sum(tr.values()))
    if tr["fade_preto"] / tot > 0.3:
        trans = "fade para preto (0,4–0,6 s) entre blocos"
    elif tr["dissolve"] / tot > 0.35:
        trans = "dissolve/crossfade (0,3–0,5 s)"
    else:
        trans = "corte seco (sem transição); whoosh suave só em troca de capítulo"
    canvas = "1080x1920" if vertical else "1280x720"
    tam_letra = m["texto"]["altura_faixa_pct_tela"]
    alt = 1920 if vertical else 720
    size = int(min(max(alt * tam_letra / 100 * 0.8, 40), 120)) if tam_letra else (64 if vertical else 52)
    pos = "inferior" if m["texto"]["inferior"] >= m["texto"]["central"] else "central"
    y = int(alt * (0.80 if pos == "inferior" else 0.5))
    return {
        "canvas": canvas,
        "plano_alvo_s": round(plano, 2),
        "cortes_por_minuto_alvo": round(cpm, 1),
        "fonte_google": fonte, "fonte_porque": porque,
        "cor_fundo": m["imagem"]["paleta"][0]["hex"] if m["imagem"]["paleta"] else "#000000",
        "cor_destaque": m["imagem"]["cor_destaque"] or "#ffd400",
        "transicao": trans,
        "legenda": {"posicao": pos, "y": y, "size": size, "pct_quadros_com_texto": txt},
        "musica": m["audio"].get("tem_musica", False),
        "loudness_alvo_lufs": -14.0,
    }


def escrever_md(m, r, destino):
    v, c, im, tx, au, ld = m["video"], m["cortes"], m["imagem"], m["texto"], m["audio"], m["loudness"]
    pal = " · ".join(f"`{p['hex']}` ({p['peso_pct']}%)" for p in im["paleta"])
    L = [
        f"# Estilo medido — {m['arquivo']}",
        "",
        "Medição automática (`medir_estilo.py`, zero token). Números aproximados; texto e música são heurísticas.",
        "",
        "## Vídeo",
        f"- Duração: **{v['duracao_s']} s** · {v['largura']}x{v['altura']} ({m['proporcao']}) · {v['fps']} fps",
        "",
        "## Ritmo",
        f"- Cortes detectados (scene > 0,3): **{c['n']}** → **{c['por_minuto']} cortes/min**",
        f"- Duração média do plano: **{c['plano_medio_s']} s** (mediana {c['plano_mediana_s']} s; mais curto "
        f"{c['plano_min_s']} s, mais longo {c['plano_max_s']} s)",
        f"- Transições: seco {c['transicoes']['seco']} · dissolve {c['transicoes']['dissolve']} · "
        f"fade p/ preto {c['transicoes']['fade_preto']}",
        "",
        "## Imagem",
        f"- Paleta (5 cores dominantes): {pal}",
        f"- Cor de destaque provável: `{im['cor_destaque']}`",
        f"- Brilho médio: **{im['brilho_medio']}**/255 · contraste (desvio da luma): **{im['contraste']}** · "
        f"saturação média: **{im['saturacao_media']}**",
        "",
        "## Texto na tela (heurística de bordas)",
        f"- Quadros com faixa de texto — centro: **{tx['central']}%** · terço inferior: **{tx['inferior']}%**",
        f"- Altura típica da faixa de texto: ~{tx['altura_faixa_pct_tela']}% da altura da tela",
        "",
        "## Áudio",
        f"- Loudness: **{ld['integrado_lufs']} LUFS** integrado · LRA {ld['faixa_lra_lu']} LU · pico {ld['pico_dbfs']} dBFS",
        f"- Tipo: **{au.get('tipo')}** (pausas silenciosas {au.get('pausas_pct')}%, chão {au.get('chao_rel_db')} dB)",
        f"- BPM aproximado: {au.get('bpm_aprox') or 'não confiável'} (confiança {au.get('bpm_confianca')})",
        "",
        "Contact-sheet: `sheet-medido.jpg` (20 quadros, 5x4).",
        "",
        "## Como recriar no Estúdio",
        f"- **Canvas**: `\"canvas\": {{\"w\": {r['canvas'].split('x')[0]}, \"h\": {r['canvas'].split('x')[1]}, \"fps\": 30}}`.",
        f"- **Ritmo de cortes alvo**: ~{r['cortes_por_minuto_alvo']} cortes/min → troque de imagem/cena a cada "
        f"**~{r['plano_alvo_s']} s** (itens da trilha `imagens` com `start` espaçado nesse passo; varie ±30%).",
        f"- **Fonte (Google Fonts, OFL)**: {r['fonte_google']} — {r['fonte_porque']}. Coloque o .ttf em `fonts/` e "
        f"declare em `\"fonts\"` do edit.json.",
        f"- **Cores**: fundo `{r['cor_fundo']}`, destaque `{r['cor_destaque']}` (use em `hl_color` / param "
        f"`cor_destaque`), texto `#ffffff` se o fundo for escuro, `#111111` se claro.",
        f"- **Legenda/texto**: posição {r['legenda']['posicao']} (`\"y\": {r['legenda']['y']}`), "
        f"`\"size\": {r['legenda']['size']}`; texto aparece em ~{r['legenda']['pct_quadros_com_texto']}% dos quadros"
        + (" — texto quase sempre na tela: legenda contínua OU texto desenhado no cenário (confira no sheet-medido.jpg)." if r['legenda']['pct_quadros_com_texto'] > 50 else
           " — texto só em títulos/destaques, não legenda contínua."),
        f"- **Transição**: {r['transicao']}.",
        f"- **Áudio**: {'música de fundo baixinha (−20 a −24 dB sob a voz, com ducking)' if r['musica'] else 'só voz, sem trilha'}"
        f"; normalize o final em {r['loudness_alvo_lufs']} LUFS. SFX: só whoosh suave (proibido impact/pop).",
        "",
    ]
    destino.write_text("\n".join(L), encoding="utf-8")


# ---------------------------------------------------------------- principal
def medir(video):
    video = Path(video).resolve()
    pasta = video.parent
    info = sondar(video)
    dur = info["duracao_s"]
    print(f"[1/5] {video.name}: {dur}s {info['largura']}x{info['altura']}")

    cortes = detectar_cortes(video)
    limites = [0.0] + [t for t in cortes if 0 < t < dur] + [dur]
    planos = np.diff(limites) if dur else np.array([0.0])
    print(f"[2/5] cortes: {len(cortes)}")

    fps_cor = min(4.0, 600 / max(dur, 1))
    rgb = quadros(video, info, fps_cor, 160)
    luma = rgb.astype(np.float32).mean(axis=3) if len(rgb) else np.zeros((1, 1, 1))
    pal = paleta(rgb) if len(rgb) else []
    trans = tipo_transicao(rgb.astype(np.float32), fps_cor, cortes)
    print("[3/5] cor e transições ok")

    fps_txt = min(1.0, 240 / max(dur, 1))
    cinza = quadros(video, info, fps_txt, 480, cinza=True)
    texto = faixas_de_texto(cinza) if len(cinza) else {"central": 0, "inferior": 0, "altura_faixa_pct_tela": 0}
    print("[4/5] texto ok")

    ld = loudness(video) if info["tem_audio"] else {"integrado_lufs": None, "faixa_lra_lu": None, "pico_dbfs": None}
    au = analisar_audio(ler_audio(video)) if info["tem_audio"] else {"tipo": "sem áudio", "tem_musica": False}
    print("[5/5] áudio ok")

    m = {
        "arquivo": video.name,
        "video": info,
        "proporcao": proporcao(info["largura"], info["altura"]),
        "cortes": {
            "n": len(cortes), "tempos_s": cortes,
            "por_minuto": round(len(cortes) / (dur / 60), 1) if dur else 0,
            "plano_medio_s": round(float(planos.mean()), 2),
            "plano_mediana_s": round(float(np.median(planos)), 2),
            "plano_min_s": round(float(planos.min()), 2), "plano_max_s": round(float(planos.max()), 2),
            "transicoes": trans,
        },
        "imagem": {
            "paleta": pal, "cor_destaque": destaque_saturado(rgb) or cor_destaque(pal),
            "brilho_medio": round(float(luma.mean()), 1),
            "contraste": round(float(luma.reshape(len(luma), -1).std(axis=1).mean()), 1),
            "saturacao_media": round(saturacao_media(rgb), 3) if len(rgb) else 0,
        },
        "texto": texto,
        "loudness": ld,
        "audio": au,
    }
    m["recomendacao"] = recomendar(m)
    sheet = pasta / "sheet-medido.jpg"
    m["sheet"] = sheet.name if contact_sheet(video, dur, sheet) else None
    (pasta / "ESTILO-MEDIDO.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    escrever_md(m, m["recomendacao"], pasta / "ESTILO-MEDIDO.md")
    print(f"OK -> {pasta / 'ESTILO-MEDIDO.md'}")
    return m


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python medir_estilo.py <video.mp4>")
        sys.exit(1)
    medir(sys.argv[1])
