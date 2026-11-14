# vozes.py — aba "🎙 Minhas vozes" do Estúdio: vozes clonadas (motor local Qwen3-TTS Base) + vozes do VoiceStudio.
# Escrito do zero. Clone = 1 áudio de referência curto (10–30 s, cortado numa pausa real) + a transcrição SÓ desse trecho
# (memória do usuário: referência longa = geração lenta; texto desalinhado = a voz "fala" a referência no meio do texto).
# Voz clonada fica em EDITOR VIDEOS\vozes\<id>\ (ref.wav + ref.txt + voz.json + teste.wav) e vira "clone:<id>" nas outras abas.
import json
import os
import re
import shutil
import sqlite3
import subprocess
import time
import unicodedata
from pathlib import Path

from .util import log

EDITOR = Path(__file__).resolve().parent.parent.parent
VOZES = EDITOR / "vozes"
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
VS_DIR = Path(os.environ.get("APPDATA", "")) / "OmniVoice"   # dados do app VoiceStudio (só leitura)
FRASE_TESTE = "Oi! Essa é a minha voz no Estúdio. Agora todo vídeo pode sair narrado por mim."


def _sl(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "voz"


def _dur(f):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                    capture_output=True, text=True, timeout=30, creationflags=NOWIN).stdout.strip())
    except Exception:
        return 0.0


def motor_clone():
    """→ (ok, motivo). Clone usa o Qwen3-TTS Base que já está instalado no PC."""
    from . import tts
    if not tts.QWEN_PY.exists() or not (tts.QWEN_DIR / "falar.py").exists():
        return False, "Falta o Qwen3-TTS (C:\\AI\\qwen3-tts com venv e falar.py)."
    hub = Path.home() / ".cache" / "huggingface" / "hub" / "models--Qwen--Qwen3-TTS-12Hz-1.7B-Base"
    if not hub.exists():
        return False, "Falta baixar o modelo Qwen3-TTS-12Hz-1.7B-Base (~4 GB) no Qwen3-TTS."
    return True, "Qwen3-TTS Base (no seu PC, placa de vídeo)"


def clones():
    out = []
    for d in sorted(VOZES.glob("*/voz.json")):
        try:
            v = json.loads(d.read_text(encoding="utf-8"))
        except Exception:
            continue
        v["tem_teste"] = (d.parent / "teste.wav").exists()
        out.append(v)
    return sorted(out, key=lambda v: -(v.get("criado") or 0))


def ref_de(vid):
    f = VOZES / Path(vid).name / "ref.wav"
    return f if f.exists() else None


def voicestudio():
    """Vozes clonadas no app VoiceStudio (lê o banco em modo só-leitura; não mexe em nada lá)."""
    db = VS_DIR / "omnivoice.db"
    if not db.exists():
        return []
    try:
        c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True, timeout=2)
        rows = c.execute("select id,name,ref_audio_path,ref_text,language,description from voice_profiles "
                         "where kind='clone' and coalesce(ref_audio_path,'')<>'' and coalesce(ref_text,'')<>''").fetchall()
        c.close()
    except Exception as e:
        log(f"VoiceStudio: não li o banco ({str(e)[:80]})")
        return []
    out = []
    for vid, nome, ref, txt, lang, desc in rows:
        f = Path(ref) if Path(ref).is_absolute() else VS_DIR / "voices" / ref
        if not f.exists():
            continue
        g = re.search(r"gender:([FM])", desc or "")
        out.append({"id": vid, "nome": nome, "idioma": lang or "", "genero": {"F": "feminina", "M": "masculina"}.get(g.group(1)) if g else "",
                    "arquivo": str(f), "importada": (VOZES / ("vs-" + vid) / "voz.json").exists()})
    return sorted(out, key=lambda v: v["nome"].lower())


def _corte_na_pausa(src: Path, alvo_min=10.0, alvo_max=20.0):
    """Onde cortar: fim de uma pausa real (silencedetect) entre alvo_min e alvo_max s; sem pausa → alvo_max."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, creationflags=NOWIN)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    boas = [t for t in ini if alvo_min <= t <= alvo_max]
    return (max(boas) + 0.15) if boas else alvo_max


def preparar_ref(src: Path, pasta: Path, inicio=0.0):
    """Converte pra wav 24 kHz mono, tira silêncio do começo, corta numa pausa (10–25 s) e normaliza o volume."""
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = pasta / "_bruto.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{inicio:.2f}", "-i", str(src), "-t", "60", "-vn", "-ac", "1", "-ar", "24000",
                    "-af", "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.1", str(tmp)],
                   check=True, timeout=180, creationflags=NOWIN)
    d = _dur(tmp)
    if d < 6:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"O áudio tem só {d:.0f} s de fala. Mande de 10 a 30 segundos de você falando (sem música).")
    fim = min(d, _corte_na_pausa(tmp)) if d > 20 else d
    ref = pasta / "ref.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-t", f"{fim:.2f}", "-af", "loudnorm=I=-18:TP=-2:LRA=11,afade=t=out:st=%.2f:d=0.15" % max(0, fim - 0.15),
                    "-ar", "24000", "-ac", "1", str(ref)], check=True, timeout=180, creationflags=NOWIN)
    tmp.unlink(missing_ok=True)
    return ref, _dur(ref)


def transcrever_ref(ref: Path, idioma="pt"):
    from .transcrever import transcrever
    words = transcrever(ref, ref.parent / "_words.json", idioma=idioma)
    (ref.parent / "_words.json").unlink(missing_ok=True)
    ws = words.get("words") if isinstance(words, dict) else words
    txt = " ".join(str(w.get("w") or w.get("word") or w.get("text") or "").strip() for w in (ws or [])).strip()
    txt = re.sub(r"\s+([,.!?;:])", r"\1", txt)
    return txt


def sintetizar(vid_ou_ref, texto: str, saida: Path, timeout=1800):
    """Fala `texto` com a voz clonada (Qwen3-TTS Base + referência). saida = .wav"""
    from . import tts
    ref = Path(vid_ou_ref) if str(vid_ou_ref).lower().endswith(".wav") else ref_de(vid_ou_ref)
    if not ref or not ref.exists():
        raise RuntimeError("Voz clonada não encontrada (a pasta da voz foi apagada?).")
    saida.parent.mkdir(parents=True, exist_ok=True)
    tf = saida.parent / "_texto_clone.txt"
    tf.write_text(texto, encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([str(tts.QWEN_PY), str(tts.QWEN_DIR / "falar.py"), "--texto", "@" + str(tf), "--ref", str(ref), "--saida", str(saida),
                        "--device", "cuda"], cwd=str(tts.QWEN_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, env=env, creationflags=NOWIN)
    tf.unlink(missing_ok=True)
    shutil.rmtree(saida.parent / "_partes", ignore_errors=True)
    if r.returncode != 0 or not saida.exists():
        raise RuntimeError("O Qwen3-TTS não gerou o áudio:\n" + "\n".join(((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-8:]))
    return saida


def criar_clone(nome, src: Path, prog=None, inicio=0.0, consentimento=False, vid=None, ref_txt=None):
    prog = prog or (lambda p, m: None)
    if not consentimento:
        raise ValueError("Marque que a voz é sua (ou de quem te autorizou por escrito).")
    ok, motivo = motor_clone()
    if not ok:
        raise RuntimeError("Clonar voz ainda não funciona neste PC: " + motivo)
    vid = vid or (_sl(nome) + "-" + time.strftime("%H%M%S"))
    pasta = VOZES / vid
    try:
        prog(8, "Preparando o seu áudio (cortando numa pausa, ajustando volume)…")
        ref, dur = preparar_ref(Path(src), pasta, inicio)
        prog(30, f"Transcrevendo os {dur:.0f} s de referência (Whisper)…")
        txt = ref_txt or transcrever_ref(ref)
        if len(txt.split()) < 8:
            raise ValueError("Quase não deu pra entender fala nesse áudio. Use um trecho com você falando claro, sem música.")
        (pasta / "ref.txt").write_text(txt, encoding="utf-8")
        info = {"id": vid, "nome": nome.strip()[:50] or vid, "motor": "qwen3-clone", "criado": time.time(), "ref_seg": round(dur, 1),
                "ref_texto": txt, "origem": Path(src).name}
        (pasta / "voz.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        prog(45, "Gerando a frase de teste com a voz clonada (1ª vez carrega o modelo, ~1 min)…")
        t = time.time()
        sintetizar(vid, FRASE_TESTE, pasta / "teste.wav")
        info["teste_seg"] = round(time.time() - t, 1)
        (pasta / "voz.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        prog(100, "Voz pronta!")
        return info
    except Exception:
        if not (pasta / "teste.wav").exists():
            shutil.rmtree(pasta, ignore_errors=True)
        raise


def importar_voicestudio(vs_id, prog=None):
    v = next((x for x in voicestudio() if x["id"] == vs_id), None)
    if not v:
        raise ValueError("Voz do VoiceStudio não encontrada.")
    pasta = VOZES / ("vs-" + vs_id)
    pasta.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(f"file:{(VS_DIR / 'omnivoice.db').as_posix()}?mode=ro", uri=True, timeout=2)
    txt = db.execute("select ref_text from voice_profiles where id=?", (vs_id,)).fetchone()[0]
    db.close()
    # a referência do VoiceStudio já vem curta e cortada em pausa: só converte (não corta de novo, o texto bate com o clipe)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v["arquivo"], "-ac", "1", "-ar", "24000", str(pasta / "ref.wav")],
                   check=True, timeout=120, creationflags=NOWIN)
    (pasta / "ref.txt").write_text(txt.strip(), encoding="utf-8")
    info = {"id": "vs-" + vs_id, "nome": v["nome"], "motor": "qwen3-clone", "criado": time.time(), "ref_seg": round(_dur(pasta / "ref.wav"), 1),
            "ref_texto": txt.strip(), "origem": "VoiceStudio", "genero": v.get("genero")}
    (pasta / "voz.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def apagar(vid):
    p = VOZES / Path(vid).name
    if p.exists() and (p / "voz.json").exists():
        shutil.rmtree(p, ignore_errors=True)
