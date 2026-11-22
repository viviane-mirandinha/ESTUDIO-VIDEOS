# blender_api.py — rotas do painel para a opção "Blender 3D" (kit em kits/blender-3d).
# Fica em arquivo separado: o server.py só chama registrar(app, globals()) uma vez.
# Fluxo: criar (roteiro → voz → palavras → plano de cenas) → prévias (1 quadro por cena) → revisar/aprovar → renderizar.
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from fastapi import Body, HTTPException
from fastapi.responses import FileResponse

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "kits" / "blender-3d"
sys.path.insert(0, str(KIT))   # gerar_cena (valores aceitos, validação do plano)
import gerar_cena as GC  # noqa: E402

TIPO = "blender"
ETAPAS = ("preparando", "plano", "previas", "revisao", "aprovado", "renderizando", "pronto", "erro")


def _ler_json(f: Path, padrao=None):
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _config():
    return json.loads((KIT / "config.json").read_text(encoding="utf-8"))


def registrar(app, G):
    """G = globals() do server.py (usa start_job, rodar_proc, out_dir, JOBS… na hora da chamada)."""
    PY = sys.executable

    def pasta_do_pid(pid: str) -> Path:
        p = G["_decode_pid"](pid)
        if not p.is_dir() or not (p / "pedido.json").exists() or (_ler_json(p / "pedido.json", {}) or {}).get("tipo") != TIPO:
            raise HTTPException(404, "Projeto Blender não encontrado.")
        return p

    def job_ativo(proj: Path):
        pid = G["pid_of"](proj)
        for j in G["JOBS"].values():
            if j.get("pid") == pid and str(j.get("tipo", "")).startswith(TIPO) and not j.get("done"):
                return {"id": j["id"], "tipo": j["tipo"], "status": j.get("status"), "pct": j.get("pct"), "msg": j.get("msg")}
        return None

    def ultimo_erro(proj: Path):
        pid = G["pid_of"](proj)
        js = sorted([j for j in G["JOBS"].values() if j.get("pid") == pid and str(j.get("tipo", "")).startswith(TIPO)], key=lambda j: j.get("criado") or 0)
        return js[-1].get("error") if js and js[-1].get("status") == "erro" else None

    def aprovacao(proj: Path) -> dict:
        return _ler_json(proj / "blender" / "aprovacao.json", {"cenas": {}}) or {"cenas": {}}

    def gravar_aprovacao(proj: Path, a: dict):
        (proj / "blender").mkdir(exist_ok=True)
        (proj / "blender" / "aprovacao.json").write_text(json.dumps(a, ensure_ascii=False, indent=2), encoding="utf-8")

    def video_final(proj: Path):
        f = proj / "final.mp4"
        return str(f) if f.exists() else None

    def _manual(proj: Path) -> bool:
        f = proj / "cena3d.tsx"
        return f.exists() and GC.MARCA not in f.read_text(encoding="utf-8")

    def estado(proj: Path) -> dict:
        pid = G["pid_of"](proj)
        job = job_ativo(proj)
        plano = _ler_json(proj / "plano.json")
        norm = _ler_json(proj / "blender" / "plano.normalizado.json")
        pv = _ler_json(proj / "previa" / "previas.json", []) or []
        ap = aprovacao(proj)
        cenas = (plano or {}).get("cenas") or []
        aprovadas = {int(k) for k, v in ap["cenas"].items() if v == "aprovada"}
        if video_final(proj) and not (job and job["tipo"] == TIPO + "_render"):
            etapa = "pronto"
        elif job and job["tipo"] == TIPO + "_render":
            etapa = "renderizando"
        elif job and job["tipo"] == TIPO + "_preparar":
            etapa = "preparando"
        elif job and job["tipo"] == TIPO + "_previas":
            etapa = "previas"
        elif job and job["tipo"] == TIPO + "_claude":
            etapa = "claude"
        elif not plano:
            etapa = "erro" if ultimo_erro(proj) else "preparando"
        elif not pv:
            etapa = "erro" if ultimo_erro(proj) else "plano"
        elif cenas and len(aprovadas) >= len(cenas):
            etapa = "aprovado"
        else:
            etapa = "revisao"
        mt = lambda f: int(f.stat().st_mtime) if f.exists() else 0
        previas = [{**i, "url": f"/api/blender/{pid}/previa/{i['cena']}?v={mt(proj / 'previa' / i['arquivo'])}"} for i in pv]
        return {"pid": pid, "nome": proj.name, "pasta": str(proj), "etapa": etapa, "pedido": _ler_json(proj / "pedido.json", {}),
                "plano": plano, "plano_normalizado": norm, "previas": previas, "aprovacao": ap, "job": job, "erro": ultimo_erro(proj),
                "video": video_final(proj), "cena_manual": _manual(proj),
                "resumo_claude": (proj / "CLAUDE-RESUMO.md").read_text(encoding="utf-8") if (proj / "CLAUDE-RESUMO.md").exists() else "", "tem_voz": any((proj / n).exists() for n in ("voz.mp3", "voz.wav", "voz.m4a")),
                "avisos": [l[2:].strip() for l in (proj / "DECISOES.md").read_text(encoding="utf-8").splitlines() if l.startswith("- ")] if (proj / "DECISOES.md").exists() else [],
                "roteiro": (proj / "roteiro.txt").read_text(encoding="utf-8") if (proj / "roteiro.txt").exists() else ""}

    # ------------------------------------------------------------------ jobs
    def sub(prog, lo, hi):
        """Progresso de uma etapa dentro de um trabalho maior (lo..hi)."""
        def f(p, m):
            prog(lo + p * (hi - lo) / 100, m)
        f.job = prog.job
        return f

    def cena_manual(proj: Path) -> bool:
        f = proj / "cena3d.tsx"
        return f.exists() and GC.MARCA not in f.read_text(encoding="utf-8")

    def claude_escreve(proj: Path, prog, tarefa: str, extra: str = ""):
        """Roda o Claude Code (1 por vez no PC) para escrever/ajustar plano.json e, se preciso, peças e cena3d.tsx."""
        modelo = (KIT / "PEDIDO-CLAUDE.md").read_text(encoding="utf-8")
        # o pedido completo vai num arquivo na pasta do vídeo; a linha de comando leva só uma frase
        # (prompt com várias linhas é cortado na primeira linha quando o claude é chamado por um atalho .cmd no Windows)
        pedido_md = proj / "PEDIDO-CLAUDE.md"
        pedido_md.write_text(modelo.format(pasta=str(proj), tarefa=tarefa, extra=extra), encoding="utf-8")
        prompt = f"Leia o arquivo {pedido_md} e faça exatamente o que ele pede (siga o CLAUDE.md do ESTUDIO-VIDEOS)."
        perm = ["--permission-mode", "acceptEdits", "--allowedTools", "Bash", "Read", "Glob", "Grep", "Write", "Edit"]
        r = G["_claude_rodar"](proj, prog, "Claude escrevendo a cena 3D…", prompt, cwd=REPO, perm_args=perm)
        fim = r.get("fim") or {}
        if not fim or fim.get("is_error"):
            raise RuntimeError("O Claude não terminou o trabalho.\n" + "\n".join(r.get("resto") or [str(fim.get("result") or "sem resposta")])[-1200:])
        resumo = str(fim.get("result") or "").strip()
        if resumo:
            with open(proj / "CLAUDE-RESUMO.md", "a", encoding="utf-8") as f:
                f.write(f"## {datetime.now().strftime('%d/%m %H:%M')} — {tarefa[:80]}\n\n{resumo}\n\n")
        try:
            GC.carregar_plano(proj)   # o plano que o Claude deixou precisa estar válido
        except SystemExit as e:
            raise RuntimeError("O plano que o Claude escreveu não é válido:\n" + str(e))
        return r

    def previas_todas(proj: Path, prog):
        G["rodar_proc"]([PY, KIT / "construir.py", proj, "--previa-cenas"], prog, cwd=REPO, lo=0, hi=100)

    def job_preparar(proj: Path, prog):
        ped = _ler_json(proj / "pedido.json", {}) or {}
        if ped.get("modo") != "claude":
            G["rodar_proc"]([PY, KIT / "preparar.py", proj], prog, cwd=REPO, lo=0, hi=100)
            return {"pid": G["pid_of"](proj), "name": proj.name}
        # modo Claude: o mesmo preparo grátis (roteiro, voz, palavras, rascunho do plano) + Claude refaz o plano/cena + quadros de teste
        G["rodar_proc"]([PY, KIT / "preparar.py", proj], prog, cwd=REPO, lo=0, hi=35)
        claude_escreve(proj, sub(prog, 35, 88), "Escrever a cena 3D deste vídeo (plano de cenas e, se precisar, peças e cena3d.tsx).")
        prog(88, "Gerando os quadros de teste das cenas…")
        previas_todas(proj, sub(prog, 88, 100))
        return {"pid": G["pid_of"](proj), "name": proj.name}

    def job_claude_ajuste(proj: Path, texto: str, cena: int, prog):
        extra = f"\n## Pedido do usuário (ajuste)\n{texto}\n" + (f"\nCena em foco: {cena}.\n" if cena else "")
        claude_escreve(proj, sub(prog, 0, 75), "Ajustar a cena 3D conforme o pedido do usuário (mantenha o resto como está).", extra)
        prog(75, "Atualizando os quadros de teste…")
        previas_todas(proj, sub(prog, 75, 100))
        return {"pid": G["pid_of"](proj), "name": proj.name}

    def job_previas(proj: Path, cenas, prog):
        cmd = [PY, KIT / "construir.py", proj, "--previa-cenas"]
        if cenas:
            cmd += ["--cenas", ",".join(str(int(c)) for c in cenas)]
        G["rodar_proc"](cmd, prog, cwd=REPO, lo=0, hi=100)
        return {"pid": G["pid_of"](proj), "name": proj.name}

    def job_render(proj: Path, prog):
        # 1) Blender renderiza todos os quadros na máquina de render e monta blender.mp4 + edit.json
        G["rodar_proc"]([PY, KIT / "construir.py", proj], prog, cwd=REPO, lo=0, hi=90)
        # 2) o Estúdio junta voz + legenda e renderiza o vídeo final
        prog(90, "Juntando voz e legenda…")
        G["rodar_proc"]([PY, REPO / "editor" / "build_from_edit.py", proj, "--render"], prog, cwd=REPO, lo=90, hi=100, render=(0, 100))
        return {"pid": G["pid_of"](proj), "name": proj.name, "video": video_final(proj)}

    def iniciar(tipo, titulo, fn, proj, *args):
        r = G["start_job"](fn, proj, *args, tipo=TIPO + "_" + tipo, titulo=titulo, pesado=True, pid=G["pid_of"](proj))
        return {**r, "pid": G["pid_of"](proj)}

    # ------------------------------------------------------------------ opções, predefinições e máquina de render
    @app.get("/api/blender/opcoes")
    def blender_opcoes():
        pre = []
        for f in sorted((KIT / "predefinicoes").glob("*.json")):
            d = _ler_json(f, {}) or {}
            pre.append({"id": f.stem, "nome": d.get("nome") or f.stem, "personagem": d.get("personagem", {}), "render": d.get("render", {})})
        return {"cena": {k: v for k, v in GC.ENUMS.items()}, "personagem": GC.PERSONAGEM_ENUMS, "cores": GC.CORES_CHAVES, "render": GC.RENDER_ENUMS,
                "predefinicoes": pre, "modos": ["gratis", "claude"], "claude": bool(G["_claude_exe"]())}

    @app.get("/api/blender/maquina")
    def blender_maquina():
        c = _config()
        return {"modo": c.get("modo", "remoto"), **c.get("remoto", {}), "chave_existe": Path(str(c.get("remoto", {}).get("chave", "")).replace("~", str(Path.home()))).exists()}

    @app.put("/api/blender/maquina")
    def blender_maquina_salvar(data: dict = Body(...)):
        c = _config()
        r = c.setdefault("remoto", {})
        for k in ("host", "usuario", "chave", "blender", "pasta"):
            if k in data:
                v = str(data[k]).strip()
                if not v or any(ch in v for ch in "\"'`$;|&<>\n\r"):
                    raise HTTPException(400, f"Valor inválido em '{k}'.")
                r[k] = v
        if data.get("modo") in ("remoto", "local"):
            c["modo"] = data["modo"]
        (KIT / "config.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True}

    @app.post("/api/blender/maquina/testar")
    def blender_maquina_testar():
        c = _config()
        r = c["remoto"]
        chave = str(r["chave"]).replace("~", str(Path.home()))
        res = {"ok": False, "online": False, "ssh": False, "gpu": None, "blender": None, "ms": None, "erro": None}
        if c.get("modo") == "local":
            res.update(ok=True, online=True, erro="Modo local: o render roda neste computador (bem mais lento).")
            return res
        if not Path(chave).exists():
            res["erro"] = f"Chave de acesso não encontrada: {chave}"
            return res
        script = (
            "$b = '" + r["blender"] + "'\n"
            "'GPU=' + ((nvidia-smi --query-gpu=name --format=csv,noheader 2>$null) -join ',')\n"
            "if (Test-Path $b) { 'BLENDER=' + ((& $b -b --version 2>$null | Select-Object -First 1)) } else { 'BLENDER=AUSENTE' }\n"
        )
        t0 = time.time()
        try:
            p = subprocess.run(["ssh", "-i", chave, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=8",
                                f"{r['usuario']}@{r['host']}", "powershell", "-NoProfile", "-NonInteractive", "-Command", "-"],
                               input=script, capture_output=True, text=True, timeout=45)
        except subprocess.TimeoutExpired:
            res["erro"] = "A máquina de render não respondeu (desligada, dormindo ou fora da rede?)."
            return res
        res["ms"] = int((time.time() - t0) * 1000)
        if p.returncode != 0 and "GPU=" not in p.stdout:
            res["erro"] = "Não consegui entrar na máquina de render: " + (p.stderr.strip().splitlines() or ["sem resposta"])[-1][:200]
            return res
        res.update(online=True, ssh=True)
        for linha in p.stdout.splitlines():
            if linha.startswith("GPU="):
                res["gpu"] = linha[4:].strip() or None
            elif linha.startswith("BLENDER="):
                v = linha[8:].strip()
                res["blender"] = None if v == "AUSENTE" else v
        res["ok"] = bool(res["blender"])
        if not res["blender"]:
            res["erro"] = "A máquina responde, mas não achei o Blender no caminho configurado."
        return res

    # ------------------------------------------------------------------ projetos
    @app.get("/api/blender/lista")
    def blender_lista():
        out = []
        base = G["out_dir"]()
        for d in sorted(base.iterdir(), reverse=True):
            if d.is_dir() and (d / "pedido.json").exists() and (_ler_json(d / "pedido.json", {}) or {}).get("tipo") == TIPO:
                e = estado(d)
                out.append({k: e[k] for k in ("pid", "nome", "etapa", "job", "video")} | {"tema": (e["pedido"] or {}).get("tema", ""), "n_cenas": len((e["plano"] or {}).get("cenas") or [])})
        return {"projetos": out}

    @app.post("/api/blender/criar")
    def blender_criar(data: dict = Body(...)):
        g = lambda k: str(data.get(k) or "").strip()
        modo = g("modo") or "gratis"
        if modo not in ("gratis", "claude"):
            raise HTTPException(400, "Modo inválido.")
        if modo == "claude" and not G["_claude_exe"]():
            raise HTTPException(400, "Falta o app do Claude neste PC (claude.ai/download). Use o modo grátis ou instale o Claude.")
        if not g("tema") and len(g("roteiro").split()) < 8:
            raise HTTPException(400, "Escreva o tema ou cole o roteiro (pelo menos algumas frases).")
        pre = g("predefinicao") or "padrao"
        if not (KIT / "predefinicoes" / f"{pre}.json").exists():
            raise HTTPException(400, f"A predefinição '{pre}' não existe.")
        try:
            dur = float(data.get("duracao") or 45)
        except Exception:
            dur = 45.0
        if not 10 <= dur <= 600:
            raise HTTPException(400, "A duração precisa ficar entre 10 segundos e 10 minutos.")
        aj = G["AJ"].ler()
        OUT = G["out_dir"]()
        nn = G["proximo_numero"](OUT)
        base = g("titulo") or g("tema") or g("roteiro").split(".")[0]
        proj = OUT / f"{nn:02d}-blender-{G['slug'](base, 34) or 'video'}"
        proj.mkdir(parents=True, exist_ok=True)
        ped = {"tipo": TIPO, "modo": modo, "tema": g("tema"), "roteiro": g("roteiro"), "voz": g("voz") or aj["voz"], "predefinicao": pre,
               "duracao": dur, "canal": g("canal"), "modelo_ollama": aj["modelo_ollama"], "idioma": aj["idioma"],
               "usar_ia": data.get("usar_ia") is not False, "criado": datetime.now().isoformat(timespec="seconds")}
        if g("cenario") in GC.ENUMS["cenario"]:
            ped["cenario"] = g("cenario")
        (proj / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")
        return iniciar("preparar", base[:70] + " · Blender 3D (plano)", job_preparar, proj)

    @app.get("/api/blender/{pid}")
    def blender_estado(pid: str):
        return estado(pasta_do_pid(pid))

    @app.put("/api/blender/{pid}/plano")
    def blender_plano_salvar(pid: str, data: dict = Body(...)):
        proj = pasta_do_pid(pid)
        f = proj / "plano.json"
        antes = f.read_text(encoding="utf-8") if f.exists() else None
        f.write_text(json.dumps(data.get("plano") or data, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            GC.carregar_plano(proj)
        except SystemExit as e:   # plano inválido: volta como estava e mostra o motivo
            if antes is None:
                f.unlink(missing_ok=True)
            else:
                f.write_text(antes, encoding="utf-8")
            raise HTTPException(400, str(e))
        a = aprovacao(proj)
        a["cenas"] = {}   # plano mudou: aprovações antigas não valem mais
        gravar_aprovacao(proj, a)
        return estado(proj)

    @app.post("/api/blender/{pid}/previas")
    def blender_previas(pid: str, data: dict = Body(default={})):
        proj = pasta_do_pid(pid)
        if not (proj / "plano.json").exists():
            raise HTTPException(400, "O plano de cenas ainda não está pronto.")
        if job_ativo(proj):
            raise HTTPException(409, "Este vídeo já tem um trabalho rodando.")
        cenas = [int(c) for c in (data.get("cenas") or [])]
        return iniciar("previas", proj.name[:60] + " · quadros de teste", job_previas, proj, cenas)

    @app.get("/api/blender/{pid}/previa/{n}")
    def blender_previa(pid: str, n: int):
        proj = pasta_do_pid(pid)
        f = next(iter(sorted((proj / "previa").glob(f"cena-{int(n):02d}.*"))), None)
        if not f:
            raise HTTPException(404, "Essa prévia ainda não existe.")
        return FileResponse(f, media_type="image/jpeg", headers={"Cache-Control": "no-cache"})

    @app.post("/api/blender/{pid}/ajustar")
    def blender_ajustar(pid: str, data: dict = Body(...)):
        """Muda campos de UMA cena (expressão, pose, enquadramento…). Depois é só pedir as prévias dessa cena de novo."""
        proj = pasta_do_pid(pid)
        if _manual(proj):
            raise HTTPException(400, "Esta cena foi escrita à mão pelo Claude: peça a mudança por texto (“Pedir ajuste ao Claude”).")
        n = int(data.get("cena") or 0)
        campos = data.get("campos") or {}
        f = proj / "plano.json"
        plano = _ler_json(f)
        if not plano:
            raise HTTPException(400, "Sem plano.")
        alvo = next((c for c in plano["cenas"] if int(c.get("id", 0)) == n), None)
        if not alvo:
            # o plano salvo pode não ter id: usa a posição (1, 2, 3…)
            alvo = plano["cenas"][n - 1] if 0 < n <= len(plano["cenas"]) else None
        if not alvo:
            raise HTTPException(404, "Cena não encontrada.")
        antes = f.read_text(encoding="utf-8")
        for k, v in campos.items():
            if v is None or v == "":
                alvo.pop(k, None)
            else:
                alvo[k] = v
        f.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            GC.carregar_plano(proj)
        except SystemExit as e:
            f.write_text(antes, encoding="utf-8")
            raise HTTPException(400, str(e))
        a = aprovacao(proj)
        a["cenas"][str(n)] = "ajustar"
        gravar_aprovacao(proj, a)
        return estado(proj)

    @app.post("/api/blender/{pid}/pedir-ajuste")
    def blender_pedir_ajuste(pid: str, data: dict = Body(...)):
        """Modo Claude: o usuário descreve a mudança em texto; o Claude mexe no plano/cena e os quadros de teste são refeitos."""
        proj = pasta_do_pid(pid)
        texto = str(data.get("texto") or "").strip()
        if len(texto) < 5:
            raise HTTPException(400, "Descreva o que você quer mudar (pelo menos uma frase curta).")
        if not G["_claude_exe"]():
            raise HTTPException(400, "Falta o app do Claude neste PC (claude.ai/download).")
        if job_ativo(proj):
            raise HTTPException(409, "Este vídeo já tem um trabalho rodando.")
        cena = int(data.get("cena") or 0)
        a = aprovacao(proj)
        if cena:
            a["cenas"][str(cena)] = "ajustar"
        else:
            a["cenas"] = {}
        gravar_aprovacao(proj, a)
        return iniciar("claude", proj.name[:60] + " · ajuste pelo Claude", job_claude_ajuste, proj, texto, cena)

    @app.post("/api/blender/{pid}/aprovar")
    def blender_aprovar(pid: str, data: dict = Body(...)):
        """acao 'proxima' = aprova esta cena e mostra a seguinte; 'tudo' = aprova esta e todas as outras e já manda renderizar."""
        proj = pasta_do_pid(pid)
        plano = _ler_json(proj / "plano.json") or {}
        total = len(plano.get("cenas") or [])
        n = int(data.get("cena") or 0)
        acao = data.get("acao") or "proxima"
        if not 1 <= n <= total:
            raise HTTPException(400, "Cena inválida.")
        if acao not in ("proxima", "tudo"):
            raise HTTPException(400, "Ação inválida.")
        if not (proj / "previa" / "previas.json").exists():
            raise HTTPException(400, "Gere os quadros de teste antes de aprovar.")
        a = aprovacao(proj)
        if acao == "tudo":
            for i in range(1, total + 1):
                a["cenas"][str(i)] = "aprovada"
        else:
            a["cenas"][str(n)] = "aprovada"
        gravar_aprovacao(proj, a)
        pendentes = [i for i in range(1, total + 1) if a["cenas"].get(str(i)) != "aprovada"]
        if acao == "tudo":
            if job_ativo(proj):
                raise HTTPException(409, "Este vídeo já tem um trabalho rodando.")
            return {**iniciar("render", proj.name[:60] + " · render Blender 3D", job_render, proj), "aprovado": True, "proxima": None}
        proxima = next((i for i in pendentes if i > n), pendentes[0] if pendentes else None)
        return {"aprovado": not pendentes, "proxima": proxima, "pendentes": pendentes}

    @app.post("/api/blender/{pid}/renderizar")
    def blender_renderizar(pid: str, data: dict = Body(default={})):
        proj = pasta_do_pid(pid)
        plano = _ler_json(proj / "plano.json") or {}
        total = len(plano.get("cenas") or [])
        a = aprovacao(proj)
        faltam = [i for i in range(1, total + 1) if a["cenas"].get(str(i)) != "aprovada"]
        if faltam and not data.get("forcar"):
            raise HTTPException(400, f"Faltam aprovar as cenas {faltam}. Aprove uma a uma ou use 'aprovar e fazer tudo'.")
        if job_ativo(proj):
            raise HTTPException(409, "Este vídeo já tem um trabalho rodando.")
        return iniciar("render", proj.name[:60] + " · render Blender 3D", job_render, proj)
