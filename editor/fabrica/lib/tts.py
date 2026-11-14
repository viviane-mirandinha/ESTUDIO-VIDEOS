# tts.py — locução local. Ordem automática: Qwen3-TTS → Chatterbox (porta 8020) → edge-tts.
import asyncio
import os
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .util import log, run, duracao_audio

os.environ["PYTHONIOENCODING"] = "utf-8"   # Qwen3 (falar.py) quebrava com 'charmap' no console do Windows
os.environ["PYTHONUTF8"] = "1"

QWEN_DIR = Path(r"C:\AI\qwen3-tts")
QWEN_PY = QWEN_DIR / "venv" / "Scripts" / "python.exe"
CHATTERBOX_URL = "http://127.0.0.1:8020"
EDGE_VOZ = "pt-BR-ThalitaMultilingualNeural"   # Antonio/Francisca são robóticas: proibidas (07/11)
EDGE_PROIBIDAS = ("pt-BR-AntonioNeural", "pt-BR-FranciscaNeural")


FISH_URL = "https://api.fish.audio"


def fish_chave():
    """Chave do Fish Audio: variável FISH_API_KEY ou a salva em Ajustes (fish_key)."""
    k = (os.environ.get("FISH_API_KEY") or "").strip()
    if not k:
        try:
            from . import ajustes as AJ
            k = str(AJ.ler().get("fish_key") or "").strip()
        except Exception:
            pass
    return k


def fish_modelo():
    """Modelo do Fish Audio (⚙ Ajustes → Fish Audio). Padrão drama-3."""
    try:
        from . import ajustes as AJ
        return str(AJ.ler().get("fish_modelo") or "").strip() or "drama-3"
    except Exception:
        return "drama-3"


def _fish(texto: str, saida: Path, voz=None):
    """Fish Audio (nuvem): uma chamada por bloco de ~1000 caracteres (em frase inteira) e junta tudo num mp3."""
    k = fish_chave()
    if not k:
        raise RuntimeError("sem chave do Fish Audio (cole em Ajustes → Fish Audio)")
    frases = [f for f in re.split(r"(?<=[.!?…])\s+", texto.strip()) if f]
    blocos, atual = [], ""
    for f in frases:
        if atual and len(atual) + len(f) > 1000:
            blocos.append(atual)
            atual = ""
        atual = (atual + " " + f).strip()
    if atual:
        blocos.append(atual)
    partes = []
    for i, b in enumerate(blocos):
        corpo = {"text": b, "format": "mp3", "mp3_bitrate": 128, "normalize": True, "latency": "normal"}
        if voz:
            corpo["reference_id"] = voz
        req = urllib.request.Request(FISH_URL + "/v1/tts", data=json.dumps(corpo).encode("utf-8"),
                                     headers={"Authorization": "Bearer " + k, "Content-Type": "application/json", "model": fish_modelo()})
        ultimo = None
        for tent in range(3):
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    p = saida.parent / f"_fish_{i:03d}.mp3"
                    p.write_bytes(r.read())
                    partes.append(p)
                    break
            except urllib.error.HTTPError as e:
                if e.code in (401, 402, 403):   # chave errada / sem crédito: não adianta repetir
                    raise RuntimeError({401: "chave do Fish Audio inválida", 402: "sem crédito no Fish Audio"}.get(e.code, "Fish Audio recusou (HTTP 403)"))
                ultimo = e
            except Exception as e:
                ultimo = e
            import time
            time.sleep(4)
        else:
            raise RuntimeError("Fish Audio falhou: " + str(ultimo)[:150])
    lista = saida.parent / "_fish_lista.txt"
    lista.write_text(chr(10).join(f"file '{p.resolve().as_posix()}'" for p in partes), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(saida)], quiet=True)
    for p in partes:
        p.unlink(missing_ok=True)
    lista.unlink(missing_ok=True)


# ---- VoiceStudio em outro PC (Tailscale): vozes "vsremoto:<nome>" ----
VS_VOZES = {   # nome → descrição em inglês (o modelo OmniVoice entende estes atributos)
    "fem": "female, young adult, moderate pitch",
    "fem-calma": "female, middle-aged, low pitch",
    "masc": "male, young adult, moderate pitch",
    "masc-grave": "male, middle-aged, low pitch",
    "sombrio": "male, elderly, very low pitch",              # narrador sombrio/místico (aprovado pelo usuário)
    "sussurro": "male, elderly, very low pitch, whisper",    # o mesmo, sussurrado
    "grave": "male, middle-aged, very low pitch",
    "idosa": "female, elderly, low pitch",
}
VS_SEED = 7   # mesma semente = mesmo timbre a cada vez (sem ela, a voz criada muda de um áudio para outro)


def vs_remoto_url():
    try:
        from . import ajustes as AJ
        u = str(AJ.ler().get("vs_remoto_url") or "").strip().rstrip("/")
    except Exception:
        return ""
    return u if re.match(r"^https?://[^\s/]+(:\d+)?$", u) else ""


def vs_remoto_ok(timeout=3):
    u = vs_remoto_url()
    if not u:
        return None
    try:
        with urllib.request.urlopen(u + "/health", timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None


def _multipart(campos: dict):
    import uuid
    b = "----vs" + uuid.uuid4().hex
    nl = "\r\n"
    partes = [f'--{b}{nl}Content-Disposition: form-data; name="{k}"{nl}{nl}{v}{nl}' for k, v in campos.items() if v not in (None, "")]
    corpo = ("".join(partes) + f"--{b}--{nl}").encode("utf-8")
    return corpo, f"multipart/form-data; boundary={b}"


def _vsremoto(texto: str, saida: Path, voz="fem"):
    """Gera a voz no VoiceStudio do outro PC (POST /generate). voz = fem | fem-calma | masc | masc-grave | perfil_<id> (voz salva lá)."""
    u = vs_remoto_url()
    if not u:
        raise RuntimeError("Falta o endereço do VoiceStudio remoto em Ajustes.")
    campos = {"text": texto, "language": "pt"}
    if voz and voz.startswith("perfil_"):
        campos["profile_id"] = voz[7:]
    else:
        campos["instruct"] = VS_VOZES.get(voz or "fem", VS_VOZES["fem"])
        campos["seed"] = VS_SEED
    corpo, ct = _multipart(campos)
    try:
        req = urllib.request.Request(u + "/generate", data=corpo, headers={"Content-Type": ct, "User-Agent": "estudio-videos"})
        with urllib.request.urlopen(req, timeout=1800) as r:
            dados = r.read()
    except urllib.error.HTTPError as e:
        det = e.read().decode("utf-8", "replace")[:300]
        if "model_licence_required" in det:
            det = "Aceite a licença dos modelos no Model Catalogue do VoiceStudio do outro PC. " + det
        raise RuntimeError(f"VoiceStudio remoto recusou ({e.code}): {det}")
    except Exception as e:
        raise RuntimeError(f"Não consegui falar com o VoiceStudio em {u} (o outro PC está ligado e com o app aberto?): {str(e)[:150]}")
    saida.write_bytes(dados)


def disponiveis():
    d = {"qwen3": QWEN_PY.exists() and (QWEN_DIR / "falar.py").exists(), "chatterbox": False, "edge": False, "fish": bool(fish_chave()), "vsremoto": bool(vs_remoto_url())}
    try:
        with urllib.request.urlopen(CHATTERBOX_URL + "/health", timeout=2) as r:
            d["chatterbox"] = bool(json.load(r).get("ok", True))
    except Exception:
        pass
    try:
        import edge_tts  # noqa
        d["edge"] = True
    except Exception:
        pass
    return d


def _qwen3(texto_path: Path, saida: Path, voz="sohee"):
    run([QWEN_PY, QWEN_DIR / "falar.py", "--texto", "@" + str(texto_path), "--voz", voz,
         "--saida", str(saida), "--device", "cuda"], cwd=str(QWEN_DIR), timeout=1800)


def _chatterbox(texto: str, saida: Path):
    frases = [f for f in re.split(r"(?<=[.!?…])\s+", texto.strip()) if f]
    partes = []
    for i, f in enumerate(frases):
        req = urllib.request.Request(CHATTERBOX_URL + "/tts", data=json.dumps(
            {"text": f, "language_id": "pt", "exaggeration": 0.45, "cfg_weight": 0.4}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            p = saida.parent / f"_tts_{i:03d}.wav"
            p.write_bytes(r.read())
            partes.append(p)
    lista = saida.parent / "_tts_lista.txt"
    lista.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in partes), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-ar", "48000", str(saida)], quiet=True)
    for p in partes:
        p.unlink(missing_ok=True)
    lista.unlink(missing_ok=True)


def _edge(texto: str, saida: Path, voz=EDGE_VOZ, rate="+4%"):
    import edge_tts
    if voz in EDGE_PROIBIDAS:
        voz = EDGE_VOZ

    async def go():
        await edge_tts.Communicate(texto, voz, rate=rate).save(str(saida))
    import time
    for tent in range(3):   # a voz da Microsoft é online: rede instável (ex.: depois de queda de luz) → tenta de novo
        try:
            asyncio.run(go())
            return
        except Exception as e:
            if tent == 2:
                raise
            log(f"edge-tts falhou ({str(e)[:80]}), tentando de novo em 5 s…")
            time.sleep(5)


def falar(texto: str, pasta: Path, motor="auto", voz=None):
    """Gera a voz na pasta do projeto. Devolve (caminho, motor_usado)."""
    pasta = Path(pasta)
    txt = pasta / "roteiro.txt"
    txt.write_text(texto, encoding="utf-8")
    d = disponiveis()
    d["clone"] = bool(voz) and motor == "clone"
    ordem = ["qwen3", "chatterbox", "edge"] if motor == "auto" else [motor]
    erros = []
    for m in ordem:
        if not d.get(m):
            erros.append(f"{m}: indisponível")
            continue
        try:
            log(f"TTS: tentando {m}…")
            if m == "clone":   # voz clonada na aba Minhas vozes (Qwen3-TTS Base + referência)
                from . import vozes as VZ
                out = pasta / "voz.wav"
                VZ.sintetizar(voz, texto, out)
            elif m == "qwen3":
                out = pasta / "voz.wav"
                _qwen3(txt, out, voz or "sohee")
            elif m == "vsremoto":
                out = pasta / "voz.wav"
                _vsremoto(texto, out, voz or "fem")
            elif m == "fish":
                out = pasta / "voz.mp3"
                _fish(texto, out, voz)
            elif m == "chatterbox":
                out = pasta / "voz.wav"
                _chatterbox(texto, out)
            else:
                out = pasta / "voz.mp3"
                _edge(texto, out, voz or EDGE_VOZ)
            if out.exists() and duracao_audio(out) > 1:
                log(f"TTS ok ({m}): {duracao_audio(out):.1f}s")
                return out, m
            erros.append(f"{m}: saída vazia")
        except Exception as e:
            erros.append(f"{m}: {str(e)[:200]}")
            log(f"TTS {m} falhou: {str(e)[:200]}")
    raise RuntimeError("Nenhum TTS funcionou:\n" + "\n".join(erros))
