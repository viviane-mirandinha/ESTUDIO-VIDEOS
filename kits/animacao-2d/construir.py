# construir.py — pipeline do modelo animacao-2d. NADA é renderizado se uma checagem reprovar.
# Uso:  python kits/animacao-2d/construir.py <pasta-do-video> [--render]
import sys, subprocess, pathlib, shutil
K = pathlib.Path(__file__).parent; R = K.parent.parent; pasta = pathlib.Path(sys.argv[1]).resolve(); render = "--render" in sys.argv
py = sys.executable; env = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
import os; env = {**os.environ, **env}
def passo(nome, cmd):
    print(f"\n==> {nome}"); r = subprocess.run(cmd, cwd=R, env=env)
    if r.returncode: print(f"\nPARADO em «{nome}». Corrija e rode de novo (nada foi renderizado)."); sys.exit(r.returncode)
passo("1/5 montar template", [py, str(K / "embutir.py"), str(pasta)])
passo("2/5 gerar hf/index.html", [py, str(R / "editor" / "build_from_edit.py"), str(pasta)])
passo("3/5 checar movimento dos personagens", ["node", str(K / "checar_movimento.mjs"), str(pasta)])
passo("4/5 checar variedade das cenas", [py, str(K / "checar_variedade.py"), str(pasta)])
if render:
    passo("5/5 renderizar", [py, str(R / "editor" / "build_from_edit.py"), str(pasta), "--render"])
    mp4 = pasta / "final.mp4"; sheet = pasta / "sheet.jpg"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip() or 30)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"fps={20/dur:.5f},scale=426:-1,tile=5x4", "-frames:v", "1", "-q:v", "3", str(sheet)])
    r = subprocess.run(["ffmpeg", "-i", str(mp4), "-vf", "blackdetect=d=0.3:pix_th=0.1", "-an", "-f", "null", "-"], capture_output=True, text=True)
    pretos = [l for l in r.stderr.splitlines() if "black_start" in l]
    subprocess.run([py, str(K / "checar_calma.py"), str(mp4)], cwd=R, env=env)
    print("tela preta:", "NENHUMA" if not pretos else f"{len(pretos)} trecho(s) — confira"); print("conferir olhando:", sheet)
else: print("\nTudo aprovado. Para renderizar, rode de novo com --render.")
