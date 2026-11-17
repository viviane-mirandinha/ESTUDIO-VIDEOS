# preencher.py — estilo "animacao-filosofica" (kit kits/animacao-2d). Transforma a narração (words.json) em cenas desenhadas em código.
# Entrada: ctx da fábrica {nome, titulo, canal, tema, duracao, words, voz, pasta, vertical, ollama, modelo, ...}
# Saída: edit.json (template "local") + <pasta>/cenas.js + template.html. As MESMAS guardas do kit rodam aqui (movimento e variedade):
# se reprovar, tenta de novo com outra combinação; nada é renderizado reprovado.
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
KIT = RAIZ / "kits" / "animacao-2d"
sys.path.insert(0, str(KIT))
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def _rodar(cmd, nome):
    r = subprocess.run(cmd, cwd=str(RAIZ), env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0, (r.stdout + r.stderr)[-1800:]


def _ia_fabrica(ctx, PL):
    """Ollama escolhe local/texto/ícone de cada trecho (opcional; se não responder, valem as regras do planejador)."""
    oll, modelo = ctx.get("ollama"), ctx.get("modelo")
    if not oll:
        return None
    estado = {"ok": True}

    def ia(grupos):
        out = {}
        for ini in range(0, len(grupos), 8):
            if not estado["ok"]:
                break
            lote = grupos[ini:ini + 8]
            lista = "\n".join(f"{ini + j}: {PL.fala_de(g)}" for j, g in enumerate(lote))
            prompt = ("Você dirige um vídeo animado de filosofia (personagem desenhado num cenário). Para CADA trecho numerado da narração escolha:\n"
                      f"- local: um de {PL.LOCAIS}\n- txt: 1 a 3 palavras TIRADAS do trecho (a ideia principal), no máximo 22 caracteres\n"
                      f"- ic: um ícone de {PL.ICONES}\nResponda SÓ JSON: {{\"cenas\": [{{\"i\": 0, \"local\": \"...\", \"txt\": \"...\", \"ic\": \"...\"}}]}}\n\nTrechos:\n{lista}")
            try:
                d = oll._json_seguro(oll.gerar(prompt, modelo, json_mode=True, temperatura=0.3, num_predict=900, timeout=90))
            except Exception:
                estado["ok"] = False
                break
            for c in (d.get("cenas") or []):
                try:
                    i = int(c.get("i"))
                except Exception:
                    continue
                if not (0 <= i < len(grupos)):
                    continue
                nf = PL.norm(PL.fala_de(grupos[i]))
                txt = str(c.get("txt") or "").strip()
                if not txt or not all(PL.norm(p) in nf for p in txt.split()):
                    c.pop("txt", None)   # texto na tela só se sair da própria fala
                out[i] = c
        return out
    return ia


def preencher(ctx):
    import planejador as PL
    from lib import ajustes as AJ
    proj = Path(ctx["pasta"])
    vertical = bool(ctx.get("vertical"))
    idioma = (AJ.ler().get("idioma") or "pt-BR")
    shutil.copy2(KIT / "cenas_base.js", proj / "cenas.js")
    (proj / "sfx").mkdir(exist_ok=True)
    shutil.copy2(KIT / "whoosh.wav", proj / "sfx" / "whoosh.wav")
    words = ctx["words"]
    ia = _ia_fabrica(ctx, PL)
    ultimo_erro = ""
    sem_anda = False
    for tentativa in range(4):
        itens, dur = PL.planejar(words, ctx["titulo"], ctx.get("tema", ""), ctx.get("canal", ""), idioma, ia, semente=tentativa, sem_anda=sem_anda, dur=ctx["duracao"])
        extra = [{"id": f"w{k}", "src": "sfx/whoosh.wav", "start": round(max(0, it["start"] - 0.15), 2), "volume": 0.12, "label": "whoosh suave"}
                 for k, it in enumerate(itens) if k % 3 == 1]
        edit = {"version": 1, "name": ctx["nome"], "canvas": {"w": 1080 if vertical else 1280, "h": 1920 if vertical else 720, "fps": 30, "bg": "#151415"},
                "duration": dur, "template": "local", "titulo_tela": ctx["titulo"],
                "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0}, "extra": extra},
                "tracks": [{"id": "fundo", "name": "Cenas"}], "items": itens}
        if vertical:
            edit["legendas"] = PL.legendas(words)
        (proj / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
        py = sys.executable
        passos = [("montar template", [py, str(KIT / "embutir.py"), str(proj)]),
                  ("gerar página", [py, str(RAIZ / "editor" / "build_from_edit.py"), str(proj)]),
                  ("checar movimento", ["node", str(KIT / "checar_movimento.mjs"), str(proj)]),
                  ("checar variedade", [py, str(KIT / "checar_variedade.py"), str(proj)])]
        falhou = None
        for nome, cmd in passos:
            ok, saida = _rodar(cmd, nome)
            if not ok:
                falhou = (nome, saida)
                break
        if not falhou:
            print(f"ANIMACAO: {len(itens)} cenas, {len({i['props']['scene'] for i in itens})} tipos diferentes — guardas de movimento e variedade APROVADAS", flush=True)
            return edit
        ultimo_erro = f"{falhou[0]}: {falhou[1]}"
        print(f"ANIMACAO: tentativa {tentativa + 1} reprovada em «{falhou[0]}» — refazendo com outra combinação…\n{falhou[1][-500:]}", flush=True)
        if falhou[0] == "checar movimento":
            sem_anda = True
    raise RuntimeError("As checagens de qualidade do estilo reprovaram o vídeo (nada foi renderizado):\n" + ultimo_erro)
