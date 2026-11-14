# fala.py — ferramentas comuns para vídeo FALADO (Fábrica de cortes e Editor de vídeo falado). Escrito do zero.
# Tudo local: ffmpeg, numpy, faster-whisper (via transcrever.py). Zero token.
import json
import re
import subprocess
import unicodedata
import wave
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

from . import rede_yt
from .util import log, run, run_venc

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
WHISPER_LANG = {"pt-BR": "pt", "en-US": "en", "es-MX": "es", "auto": "auto"}


# ------------------------------------------------------------------ mídia
def probe(path):
    """{w, h, dur, fps, audio} do arquivo."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, creationflags=NOWIN)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    fr = v.get("r_frame_rate", "30/1").split("/")
    fps = float(fr[0]) / float(fr[1] or 1) if len(fr) == 2 and float(fr[1] or 0) else 30.0
    return {"w": int(v.get("width") or 0), "h": int(v.get("height") or 0), "dur": float((d.get("format") or {}).get("duration") or 0),
            "fps": fps, "audio": a}


def extrair_audio(video, wav, sr=16000):
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", str(wav)], quiet=True)
    return wav


def energia(wav, passo=0.5):
    """Volume (dB) a cada `passo` segundos. Devolve (lista_db, passo)."""
    with wave.open(str(wav), "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    n = int(sr * passo)
    if n <= 0 or len(x) < n:
        return [], passo
    m = len(x) // n
    blocos = x[:m * n].reshape(m, n)
    rms = np.sqrt((blocos ** 2).mean(axis=1) + 1e-12)
    return [round(float(v), 2) for v in 20 * np.log10(rms + 1e-9)], passo


def volume_medio(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NOWIN)
    m = re.search(r"mean_volume:\s*(-?[\d.]+)", r.stderr or "")
    return float(m.group(1)) if m else -25.0


def silencios(path, min_dur=0.35):
    """Trechos de silêncio [(ini, fim)]. Limiar automático = volume médio − 6 dB (limitado entre −45 e −12 dB);
    nunca dB fixo (áudio normalizado não tem silêncio abaixo de −35 dB)."""
    lim = max(-45.0, min(-12.0, volume_medio(path) - 6))
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", f"silencedetect=noise={lim:.1f}dB:d={min_dur}", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NOWIN)
    ini, out = None, []
    for ln in (r.stderr or "").splitlines():
        m = re.search(r"silence_start:\s*(-?[\d.]+)", ln)
        if m:
            ini = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end:\s*([\d.]+)", ln)
        if m and ini is not None:
            out.append((round(ini, 3), round(float(m.group(1)), 3)))
            ini = None
    return out, lim


# ------------------------------------------------------------------ texto
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", t).split()


def frases(words, gap_max=1.2):
    """Agrupa palavras em frases: termina em . ! ? … ou numa pausa longa."""
    out, g = [], []
    for i, w in enumerate(words):
        g.append(w)
        nx = words[i + 1] if i + 1 < len(words) else None
        fim = re.search(r"[.!?…]$", w["w"]) or nx is None or (nx["s"] - w["e"] > gap_max)
        if fim:
            out.append({"texto": " ".join(x["w"] for x in g), "s": g[0]["s"], "e": g[-1]["e"], "words": g, "i0": i - len(g) + 1, "i1": i})
            g = []
    return out


def parecido(a, b):
    return SequenceMatcher(None, " ".join(norm(a)), " ".join(norm(b))).ratio()


def retakes(fr):
    """Índices de frases que foram repetidas logo em seguida (o falante errou e falou de novo).
    Regra: a frase seguinte (ou a próxima depois de uma bem curta) começa igual / é muito parecida → descarta a primeira."""
    drop = set()
    for i in range(len(fr) - 1):
        a = norm(fr[i]["texto"])
        if len(a) < 2:
            continue
        for j in (i + 1, i + 2):
            if j >= len(fr):
                break
            b = norm(fr[j]["texto"])
            if not b:
                continue
            ini_igual = len(a) >= 3 and a[:3] == b[:3] and len(a) <= len(b) + 2
            sim = parecido(" ".join(a), " ".join(b[:len(a) + 2])) if a else 0
            if ini_igual or sim >= 0.78:
                for k in range(i, j):   # descarta a(s) tentativa(s) antes da boa
                    drop.add(k)
                break
    return sorted(drop)


FORTES = ("nunca", "segredo", "ninguem", "verdade", "erro", "maior", "pior", "melhor", "dinheiro", "morte", "morreu", "problema", "incrivel",
          "absurdo", "mentira", "milhao", "milhoes", "bilhao", "rico", "pobre", "medo", "chocante", "proibido", "perigo", "sempre", "jamais",
          "never", "secret", "nobody", "truth", "mistake", "worst", "best", "money", "million", "crazy", "insane",
          "nunca", "secreto", "nadie", "verdad", "peor", "mejor", "dinero")
CONECTIVOS = ("e", "mas", "entao", "ai", "porque", "tipo", "ne", "que", "isso", "nao", "sim", "olha", "cara", "bom", "entendeu", "exato",
              "and", "but", "so", "because", "yeah", "no", "y", "pero", "entonces")   # começar com isso = resposta no meio da conversa (sem contexto)
NUMERO = re.compile(r"\d|\b(um|dois|tres|quatro|cinco|dez|cem|mil|milhao|milhoes|bilhao|one|two|three|ten|hundred|thousand|million)\b")


def nota_regras(janela, ener, passo, base_db):
    """Nota 0-10 sem IA: energia da voz, gancho na 1ª frase, pergunta/número, fecho completo."""
    txt = " ".join(f["texto"] for f in janela)
    p0 = janela[0]["texto"]
    n0 = norm(p0)
    pts, motivos = 0.0, []
    a, b = int(janela[0]["s"] / passo), int(janela[-1]["e"] / passo) + 1
    seg = ener[a:b] if ener else []
    if seg:
        med = float(np.median(seg))
        pico = float(np.percentile(seg, 90))
        d = (med - base_db) + 0.5 * (pico - base_db)
        pts += max(-1.5, min(3.0, d / 2.0))
        if d > 2:
            motivos.append("fala com mais energia")
    if "?" in p0 or NUMERO.search(" ".join(n0)) or any(w in FORTES for w in n0):
        pts += 2.2
        motivos.append("começa com gancho (pergunta, número ou palavra forte)")
    if n0 and n0[0] in CONECTIVOS:
        pts -= 1.6
    if len(n0) <= 16:
        pts += 0.8
    nq = txt.count("?")
    nn = len(NUMERO.findall(" ".join(norm(txt))))
    pts += min(1.5, 0.5 * nq) + min(1.2, 0.3 * nn)
    if nq:
        motivos.append("tem pergunta")
    if nn:
        motivos.append("tem números")
    if re.search(r"[.!?…]$", janela[-1]["texto"].strip()):
        pts += 1.0
    else:
        pts -= 0.8
    forte = sum(1 for w in norm(txt) if w in FORTES)
    pts += min(1.5, 0.4 * forte)
    return round(max(0.0, min(10.0, 3.0 + pts)), 1), motivos


def janelas(fr, dmin=30, dmax=60):
    """Trechos candidatos (frases inteiras) entre dmin e dmax segundos."""
    out = []
    for i in range(len(fr)):
        for j in range(i, len(fr)):
            d = fr[j]["e"] - fr[i]["s"]
            if d > dmax:
                break
            if d >= dmin:
                out.append((i, j))
    return out


def sem_sobrepor(cands, n, folga=1.0):
    esc = []
    for c in sorted(cands, key=lambda c: -c["nota"]):
        if all(c["e"] + folga <= x["s"] or c["s"] >= x["e"] + folga for x in esc):
            esc.append(c)
        if len(esc) >= n:
            break
    return esc


def palavras_no_trecho(words, s, e, desloc):
    """Palavras dentro de [s, e] com tempo relativo (− desloc)."""
    return [{"w": w["w"], "s": round(max(0, w["s"] - desloc), 2), "e": round(max(0, w["e"] - desloc), 2)}
            for w in words if w["s"] >= s - 0.05 and w["e"] <= e + 0.3]


def cortar(src, dst, ini, dur, altura_max=1080, vertical=False):
    """Recorta [ini, ini+dur] re-encodando (30 fps constante, keyframe a cada 1 s — editor/render seguros)."""
    vf = f"fps=30,scale=-2:'min({altura_max},ih)'"
    run_venc(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini:.3f}", "-i", str(src), "-t", f"{dur:.3f}", "-vf", vf],
             ["-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(dst)],
             crf=20)
    return dst


def baixar_link(url, dst: Path, secao=None):
    """yt-dlp: tenta até 720p; se o YouTube pedir login/bot-check, cai pro cliente mweb (360p, passa sempre)."""
    base = [*rede_yt.cmd(), "--no-playlist", "--no-part", "--force-overwrites", "-o", str(dst)]
    if secao:
        base += ["--download-sections", secao]
    tent = [["-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/b[height<=720]", "--merge-output-format", "mp4"],
            ["--extractor-args", "youtube:player_client=mweb", "-f", "18/b[ext=mp4]"]]
    erro = ""
    for t in tent:
        r = subprocess.run(base + t + [url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600, creationflags=NOWIN)
        if dst.exists() and dst.stat().st_size > 100_000:
            return dst
        erro = ((r.stderr or r.stdout or "").strip().splitlines() or ["sem saída"])[-1]
        log(f"yt-dlp falhou ({erro[:120]}), tentando outro jeito…")
    el = erro.lower()
    motivo = ("o vídeo não existe, foi apagado ou está privado" if ("unavailable" in el or "private" in el or "removed" in el or "does not exist" in el)
              else "o YouTube pediu login / verificação — ligue um login em Ajustes → Downloads do YouTube" if ("sign in" in el or "login" in el or "bot" in el)
              else "o link não é de um vídeo" if ("unsupported url" in el or "is not a valid url" in el)
              else "")
    raise RuntimeError("Não consegui baixar o vídeo do link" + (f" ({motivo}). Confira se o link abre no navegador." if motivo else ".") + " Detalhe: " + erro[:200])
