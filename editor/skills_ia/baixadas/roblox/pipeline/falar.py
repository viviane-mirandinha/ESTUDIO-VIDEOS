"""falar.py - Kokoro TTS local (PT-BR), sem chave e sem internet depois do 1o download.
Uso:
  python -X utf8 falar.py texto.txt saida.mp3 [--voz pm_alex] [--speed 1.0] [--pitch 0]
  python -X utf8 falar.py --baixar      (so baixa os 2 arquivos do modelo, ~340 MB)
  python -X utf8 falar.py --amostras    (gera amostras das 3 vozes PT: pf_dora, pm_alex, pm_santa)
Precisa: pip install kokoro-onnx soundfile numpy  +  ffmpeg no PATH.
Modelo (kokoro-v1.0.onnx + voices-v1.0.bin), procurado nesta ordem:
  1) pasta da variavel ESTUDIO_KOKORO   2) pipeline\\kokoro\\ (ao lado deste arquivo)   3) ~/.cache/kokoro
  Se nao achar, baixa sozinho em ~/.cache/kokoro (release oficial do kokoro-onnx no GitHub).
"""
import argparse, os, subprocess, sys, tempfile, urllib.request
import soundfile as sf

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQS = {"kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"}
VOZES_PT = ["pf_dora", "pm_alex", "pm_santa"]
TEXTO_AMOSTRA = ("Nessa cidade, se você pula o café da manhã, você sai flutuando. "
                 "Eu? Eu sou o menino que esqueceu o cereal. E agora eu tô lá em cima, nas nuvens.")


def pasta_modelo(baixar=True):
    cands = [os.environ.get("ESTUDIO_KOKORO", ""), os.path.join(AQUI, "kokoro"),
             os.path.join(os.path.expanduser("~"), ".cache", "kokoro")]
    for c in cands:
        if c and all(os.path.exists(os.path.join(c, a)) for a in ARQS):
            return c
    if not baixar:
        return None
    dest = cands[0] or cands[2]
    os.makedirs(dest, exist_ok=True)
    for a, url in ARQS.items():
        alvo = os.path.join(dest, a)
        if not os.path.exists(alvo):
            print("baixando", a, "...", flush=True)
            urllib.request.urlretrieve(url, alvo + ".part")
            os.replace(alvo + ".part", alvo)
    return dest


_k = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        d = pasta_modelo()
        _k = Kokoro(os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin"))
    return _k


def gerar(texto, saida, voz="pf_dora", speed=1.0, pitch=0.0):
    samples, sr = kokoro().create(texto, voice=voz, speed=speed, lang="pt-br")
    fd, wav = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    sf.write(wav, samples, sr)
    af = []
    if pitch:
        f = 2 ** (pitch / 12)
        af = ["-af", f"asetrate={sr}*{f:.4f},aresample={sr},atempo={1/f:.4f}"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, *af,
                    "-c:a", "libmp3lame", "-b:a", "192k", saida], check=True)
    os.remove(wav)
    print("OK", saida)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("entrada", nargs="?"); p.add_argument("saida", nargs="?")
    p.add_argument("--voz", default="pf_dora"); p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--pitch", type=float, default=0.0, help="semitons (ex 1.5)")
    p.add_argument("--amostras", action="store_true"); p.add_argument("--baixar", action="store_true")
    a = p.parse_args()
    if a.baixar:
        print("modelo em:", pasta_modelo()); sys.exit()
    if a.amostras:
        out = os.path.join(os.getcwd(), "AMOSTRAS-KOKORO"); os.makedirs(out, exist_ok=True)
        for v in VOZES_PT:
            gerar(TEXTO_AMOSTRA, os.path.join(out, f"{v}_normal.mp3"), v, 1.0, 0)
            gerar(TEXTO_AMOSTRA, os.path.join(out, f"{v}_ref.mp3"), v, 1.25, 1.5)
        sys.exit()
    if not (a.entrada and a.saida):
        p.error("informe entrada.txt e saida.mp3")
    with open(a.entrada, encoding="utf-8") as fh:
        gerar(fh.read().strip(), a.saida, a.voz, a.speed, a.pitch)
