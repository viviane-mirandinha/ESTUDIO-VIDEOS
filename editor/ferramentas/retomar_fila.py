"""Retoma a fila de vídeos dos Estilos IA que parou (skills_ia/FILA-PARADA.json): roda o Claude sozinho em cada pasta, 1 por vez.
Grava RELATORIO.json, põe o resultado.mp4 no edit.json e troca o vídeo de exemplo do estilo no painel. Status em skills_ia/FILA-STATUS.txt."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ED = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ED / "fabrica"))
from lib import ajustes as AJ  # noqa: E402

SKI = ED / "skills_ia"
STATUS = SKI / "FILA-STATUS.txt"
PROMPT = ("Leia o PEDIDO.md desta pasta e faça o vídeo exatamente como está pedido, usando a skill indicada. "
          "Você está rodando sozinho pelo painel: não faça perguntas, decida e siga até salvar resultado.mp4. "
          "Se já houver trabalho começado nesta pasta, aproveite e continue de onde parou.")


def log(m):
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(time.strftime("%d/%m %H:%M ") + m + "\n")


def claude_exe():
    w = shutil.which("claude")
    if w:
        return w
    import os
    ach = []
    for base in (os.environ.get("LOCALAPPDATA"), os.environ.get("APPDATA")):
        if base:
            ach += [p for p in Path(base).glob("Claude-Data/*/claude-code/*/*/claude.exe") if p.is_file()]
    ach.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(ach[0]) if ach else str(Path.home() / ".local" / "bin" / "claude.exe")


def resultado(p: Path):
    f = p / "resultado.mp4"
    if f.exists():
        return f
    c = [x for x in p.rglob("*.mp4") if "entrada" not in x.relative_to(p).parts and "node_modules" not in x.parts and x.stat().st_size > 50_000]
    if not c:
        return None
    shutil.copy2(max(c, key=lambda x: x.stat().st_mtime), f)
    return f


def probe(f):
    try:
        o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(f)],
                           capture_output=True, text=True, timeout=30).stdout
        d = json.loads(o)
        s = next((x for x in d.get("streams", []) if x.get("width")), {})
        return float(d["format"]["duration"]), s.get("width"), s.get("height")
    except Exception:
        return None, None, None


def fazer(item):
    p, sk = Path(item["pasta"]), item["skill"]
    if (p / "resultado.mp4").exists():
        log(f"{p.name}: já estava pronto")
        return
    log(f"{p.name}: começando ({sk})")
    t0, fim, n = time.time(), {}, 0
    env = AJ.env_chaves({**os.environ, "PYTHONIOENCODING": "utf-8"})
    with open(p / "claude-log.jsonl", "a", encoding="utf-8") as lg:
        pr = subprocess.Popen([claude_exe(), "-p", PROMPT, "--output-format", "stream-json", "--verbose", "--permission-mode", "bypassPermissions"],
                              cwd=str(p), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              encoding="utf-8", errors="replace", env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            for line in pr.stdout:
                lg.write(line)
                if line.startswith("{"):
                    try:
                        ev = json.loads(line)
                    except Exception:
                        continue
                    if ev.get("type") == "result":
                        fim = ev
                    elif ev.get("type") == "assistant":
                        n += 1
            pr.wait(timeout=7200)
        except subprocess.TimeoutExpired:
            pr.kill()
    us = fim.get("usage") or {}
    tok = sum(int(us.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    rel_f = p / "RELATORIO.json"
    rel = json.loads(rel_f.read_text(encoding="utf-8-sig")) if rel_f.exists() else {}
    rel.update({"ferramenta_ia": f"Claude Code + skill {sk}", "minutos": round((rel.get("minutos") or 0) + (time.time() - t0) / 60, 1),
                "tokens": (rel.get("tokens") or 0) + tok or None, "custo_usd": round((rel.get("custo_usd") or 0) + (fim.get("total_cost_usd") or 0), 4),
                "passos": (rel.get("passos") or 0) + n, "observacoes": str(fim.get("result") or "")[:1500]})
    rel_f.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    vid = resultado(p)
    if not vid:
        log(f"{p.name}: ❌ terminou sem vídeo — {str(fim.get('result') or '')[:200]}")
        return
    dur, w, h = probe(vid)
    try:
        ed = json.loads((p / "edit.json").read_text(encoding="utf-8"))
        ed["duration"] = dur or ed.get("duration")
        ed["items"] = [{"id": "v1", "type": "video", "track": "fundo", "start": 0, "dur": dur or ed.get("duration"),
                        "props": {"src": "resultado.mp4", "fill": True, "fit": "cover", "volume": 1}}]
        if w and h:
            ed["canvas"].update(w=int(w), h=int(h))
        (p / "edit.json").write_text(json.dumps(ed, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:
        log(f"{p.name}: aviso edit.json: {e}")
    prev = SKI / "previews"
    (prev / "_vendedor").mkdir(parents=True, exist_ok=True)
    dst, bk = prev / f"{sk}.mp4", prev / "_vendedor" / f"{sk}.mp4"
    if dst.exists() and not bk.exists():
        shutil.move(dst, bk)
    shutil.copy2(vid, dst)
    log(f"{p.name}: ✅ pronto em {rel['minutos']} min · US$ {rel['custo_usd']} → exemplo do estilo trocado")


if __name__ == "__main__":
    fila = json.loads((SKI / "FILA-PARADA.json").read_text(encoding="utf-8"))
    log(f"retomando {len(fila)} vídeos")
    for it in fila:
        try:
            fazer(it)
        except Exception as e:
            log(f"{Path(it['pasta']).name}: ❌ erro {e}")
    log("FIM da fila")
