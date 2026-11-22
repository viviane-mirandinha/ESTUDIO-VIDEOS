# render_quadros.py — renderiza no Blender a cena "assada" (cena.glb + quadros.json).
# Pode rodar na máquina potente (SSH, padrão) ou neste computador (--local).
#   python kits/blender-3d/render_quadros.py <pasta-blender> [--local] [--de N --ate M] [--quadros 30,120]
# Os quadros voltam em <pasta-blender>/quadros/qNNNN.jpg. Mostra progresso como "@@pct|mensagem".
import json, os, re, shutil, subprocess, sys, tarfile, time, uuid
from pathlib import Path

KIT = Path(__file__).resolve().parent
CONFIG = json.loads((KIT / "config.json").read_text(encoding="utf-8"))
RENDER_PY = KIT / "render" / "renderizar.py"


def args_blender(pasta_cena: str, saida: str, extra: dict) -> list:
    q = CONFIG["quadros"]
    a = [pasta_cena, f"--saida={saida}", f"--formato={q['formato']}", f"--qualidade={q['qualidade']}", f"--amostras={q['amostras']}"]
    for k in ("de", "ate", "quadros"):
        if extra.get(k):
            a.append(f"--{k}={extra[k]}")
    return a


def progresso(linha: str, total: int):
    m = re.search(r"quadro (\d+)/(\d+)", linha)
    if m:
        print(f"@@{int(m.group(1)) * 100 // max(1, int(m.group(2)))}|Blender: quadro {m.group(1)} de {m.group(2)}", flush=True)


def achar_blender_local() -> str:
    c = CONFIG["local"].get("blender")
    if c and Path(c).exists():
        return c
    for base in (r"C:\Program Files\Blender Foundation", "/Applications/Blender.app/Contents/MacOS", "/usr/bin", "/snap/bin"):
        b = Path(base)
        if b.is_dir():
            for p in sorted(b.glob("*/blender.exe")) + sorted(b.glob("Blender")) + sorted(b.glob("blender")):
                return str(p)
    sys.exit("Não achei o Blender neste computador. Instale em blender.org ou ponha o caminho em kits/blender-3d/config.json (local.blender).")


def local(pasta: Path, extra: dict):
    blender = achar_blender_local()
    saida = pasta / "quadros"
    saida.mkdir(exist_ok=True)
    env = {**os.environ, "LARGURA": str(CONFIG["quadros"]["largura"]), "ALTURA": str(CONFIG["quadros"]["altura"])}
    cmd = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(RENDER_PY), "--", *args_blender(str(pasta), str(saida), extra)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env)
    for l in p.stdout:
        progresso(l, 0)
    if p.wait():
        sys.exit("O Blender falhou neste computador.")


def ssh_base():
    r = CONFIG["remoto"]
    chave = os.path.expanduser(r["chave"])
    if not Path(chave).exists():
        sys.exit(f"Chave de acesso não encontrada: {chave}. Veja o README (seção 'Máquina de render').")
    opts = ["-i", chave, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=30"]
    return r, opts, f"{r['usuario']}@{r['host']}"


def ps_remoto(opts, alvo, script: str, ao_vivo=False):
    """Roda um script PowerShell na máquina remota (enviado pela entrada padrão, sem problemas de aspas)."""
    p = subprocess.Popen(["ssh", *opts, alvo, "powershell", "-NoProfile", "-NonInteractive", "-Command", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    p.stdin.write(script)
    p.stdin.close()
    saida = []
    for l in p.stdout:
        saida.append(l)
        if ao_vivo:
            progresso(l, 0)
    return p.wait(), "".join(saida)


def remoto(pasta: Path, extra: dict):
    r, opts, alvo = ssh_base()
    # a máquina está ligada e na rede?
    t = subprocess.run(["ssh", *opts, alvo, "echo ok"], capture_output=True, text=True, timeout=40)
    if t.returncode or "ok" not in t.stdout:
        sys.exit(f"Não consegui falar com a máquina de render ({r['host']}). Ela está ligada e o Tailscale conectado? Detalhe: {t.stderr.strip()[-200:]}\n(Para renderizar neste computador, use --local — é bem mais lento.)")
    job = "job-" + uuid.uuid4().hex[:8]
    dir_r = r["pasta"].rstrip("\\") + "\\" + job
    dir_scp = dir_r.replace("\\", "/")
    print(f"@@2|Enviando a cena para a máquina de render…", flush=True)
    rc, o = ps_remoto(opts, alvo, f"New-Item -ItemType Directory -Force '{dir_r}' | Out-Null\n")
    if rc:
        sys.exit("Não consegui criar a pasta na máquina de render: " + o[-300:])
    for arq in (pasta / "cena.glb", pasta / "quadros.json", RENDER_PY):
        c = subprocess.run(["scp", *opts, str(arq), f"{alvo}:{dir_scp}/"], capture_output=True, text=True)
        if c.returncode:
            sys.exit(f"Falha ao enviar {arq.name}: {c.stderr[-300:]}")
    q = CONFIG["quadros"]
    ex = " ".join(f"--{k}={extra[k]}" for k in ("de", "ate", "quadros") if extra.get(k))
    script = f"""$ErrorActionPreference = 'Continue'
$env:LARGURA = '{q['largura']}'; $env:ALTURA = '{q['altura']}'
$b = '{r['blender']}'
if (-not (Test-Path $b)) {{ 'ERRO_BLENDER_AUSENTE'; exit 3 }}
& $b -b --factory-startup --python-exit-code 1 -P '{dir_r}\\renderizar.py' -- '{dir_r}' --saida='{dir_r}\\quadros' --formato={q['formato']} --qualidade={q['qualidade']} --amostras={q['amostras']} {ex} 2>&1 | ForEach-Object {{ "$_" }}
if ($LASTEXITCODE -ne 0) {{ 'ERRO_BLENDER'; exit 1 }}
tar -cf '{dir_r}\\quadros.tar' -C '{dir_r}' quadros
"FIM_OK"
"""
    t0 = time.time()
    rc, o = ps_remoto(opts, alvo, script, ao_vivo=True)
    if rc or "FIM_OK" not in o:
        sys.exit("O Blender falhou na máquina de render:\n" + "\n".join(o.splitlines()[-15:]))
    print(f"@@92|Render pronto em {int(time.time() - t0)} s. Trazendo os quadros…", flush=True)
    tar = pasta / "quadros.tar"
    c = subprocess.run(["scp", *opts, f"{alvo}:{dir_scp}/quadros.tar", str(tar)], capture_output=True, text=True)
    if c.returncode:
        sys.exit("Falha ao trazer os quadros: " + c.stderr[-300:])
    saida = pasta / "quadros"
    shutil.rmtree(saida, ignore_errors=True)
    with tarfile.open(tar) as tf:
        try:
            tf.extractall(pasta, filter="data")
        except TypeError:   # Python antigo sem o argumento filter
            tf.extractall(pasta)
    tar.unlink()
    ps_remoto(opts, alvo, f"Remove-Item -Recurse -Force '{dir_r}' -ErrorAction SilentlyContinue\n")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    pasta = Path(a[0]).resolve()
    extra = {}
    for i, x in enumerate(a):
        if x in ("--de", "--ate", "--quadros") and i + 1 < len(a):
            extra[x[2:]] = a[i + 1]
    if not (pasta / "cena.glb").exists():
        sys.exit(f"Falta {pasta / 'cena.glb'} (rode o bake antes).")
    (local if "--local" in a or CONFIG["modo"] == "local" else remoto)(pasta, extra)
    n = len(list((pasta / "quadros").glob("q*.*")))
    print(f"@@100|{n} quadros em {pasta / 'quadros'}", flush=True)


if __name__ == "__main__":
    main()
