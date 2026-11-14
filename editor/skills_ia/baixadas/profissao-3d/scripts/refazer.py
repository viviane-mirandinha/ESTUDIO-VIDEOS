r"""refazer.py - REFAZ O VIDEO INTEIRO a partir de um arquivo de voz (troca de voz = 1 comando).
  python -X utf8 refazer.py PROJETO --voz "D:\Audios\31-10\01.wav" --saida "D:\...\NN - DD-MM-AAAA - ... .mp4" [--procs 3]
Etapas: voz -> audio\voz.wav (48k mono) -> alinhar.py (palavras.json; legenda/cortes/etiquetas/SFX recalculados pelas ancoras)
        -> Blender cena.py em N processos paralelos (frames\; se palavras.json ou cena.py mudou, apaga os frames velhos)
        -> mix.py (musica + ducking + SFX) -> compor.py (bloom, etiquetas, legenda, encode) -> conferencia.jpg
Sem --voz: usa audio\voz_guia.wav (Kokoro). --pular-render: so refaz mix + legenda (quando so mudou dados.json).
Etapas ja feitas pulam sozinhas: frames prontos nao re-renderizam; --forcar-alinhar realinha mesmo sem trocar a voz.
"""
import argparse, hashlib, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
ap = argparse.ArgumentParser(); ap.add_argument("projeto"); ap.add_argument("--voz"); ap.add_argument("--saida", required=True)
ap.add_argument("--procs", type=int, default=3); ap.add_argument("--pular-render", action="store_true"); ap.add_argument("--forcar-alinhar", action="store_true")
a = ap.parse_args(); W = os.path.abspath(a.projeto); PY = [sys.executable, "-X", "utf8"]
def run(cmd): print(">>", " ".join(os.path.basename(c) if i < 3 else c for i, c in enumerate(cmd))[:160], flush=True); subprocess.run(cmd, check=True)
def md5(*ps): h = hashlib.md5(); [h.update(open(p, "rb").read()) for p in ps]; return h.hexdigest()

voz_src = a.voz or os.path.join(W, "audio", "voz_guia.wav"); voz = os.path.join(W, "audio", "voz.wav")
os.makedirs(os.path.join(W, "audio"), exist_ok=True)
tmp = voz + ".novo.wav"
run(["ffmpeg", "-y", "-v", "error", "-i", voz_src, "-ar", "48000", "-ac", "1", tmp])
mudou = not os.path.exists(voz) or md5(tmp) != md5(voz)
os.replace(tmp, voz)
if mudou or a.forcar_alinhar or not os.path.exists(os.path.join(W, "palavras.json")):
    run(PY + [os.path.join(HERE, "alinhar.py"), W, voz])

if not a.pular_render:
    fr = os.path.join(W, "frames"); chave = md5(os.path.join(W, "palavras.json"), os.path.join(W, "cena.py"), os.path.join(W, "projeto.json"))
    ck = os.path.join(fr, "_chave.txt")
    if os.path.exists(fr) and (not os.path.exists(ck) or open(ck).read() != chave):
        print("cortes mudaram -> apagando frames velhos"); shutil.rmtree(fr)
    os.makedirs(fr, exist_ok=True); open(ck, "w").write(chave)
    out = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(W, "cena.py"), "--", W, "list"], capture_output=True, text=True).stdout
    NF = int([l for l in out.splitlines() if l.startswith("END")][0].split()[-1])
    n = a.procs; parts = [(NF * k // n, NF * (k + 1) // n) for k in range(n)]
    t0 = time.time()
    # Blender 5.2 as vezes da EXCEPTION_ACCESS_VIOLATION no depsgraph (aleatorio; o mesmo quadro renderiza ao repetir).
    # Como quadros prontos sao pulados, um processo que cai e simplesmente relancado (ate 6x por parte).
    def lanca(k, f0, f1):
        return subprocess.Popen([BLENDER, "-b", "--factory-startup", "--python", os.path.join(W, "cena.py"), "--", W, "frames", str(f0), str(f1)],
                                stdout=open(os.path.join(W, f"render_{k}.log"), "a"), stderr=subprocess.STDOUT)
    ps = [lanca(k, f0, f1) for k, (f0, f1) in enumerate(parts)]; tent = [0] * n
    while True:
        time.sleep(30); feitos = len([x for x in os.listdir(fr) if x.endswith(".png")])
        print(f"render {feitos}/{NF} ({feitos / max(1, time.time() - t0):.2f} q/s)", flush=True)
        for k, p in enumerate(ps):
            if p.poll() not in (None, 0) and tent[k] < 6:
                tent[k] += 1; print(f"parte {k} caiu (codigo {p.returncode}) -> relancando ({tent[k]}/6)", flush=True); ps[k] = lanca(k, *parts[k])
        if all(p.poll() is not None for p in ps): break
    if any(p.returncode for p in ps): raise SystemExit("render falhou: ver render_*.log")
run(PY + [os.path.join(HERE, "mix.py"), W])
run(PY + [os.path.join(HERE, "compor.py"), W, a.saida])
