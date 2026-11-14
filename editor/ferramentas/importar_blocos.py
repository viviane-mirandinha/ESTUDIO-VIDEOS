"""importar_blocos.py — copia blocos do registry oficial do HyperFrames (Apache-2.0) para templates/blocos/.

Uso:
  python ferramentas/importar_blocos.py                 # importa a lista padrão (BLOCOS abaixo)
  python ferramentas/importar_blocos.py lt-clean-bar    # importa só os nomes dados

Cada bloco vira templates/blocos/<nome>/ com:
  <nome>.html   (arquivo original do registry, sem mudanças)
  assets/...    (fontes/scripts que o bloco usa)
  bloco.json    (título PT, descrição, duração, tamanho, variáveis, origem, licença)
e templates/blocos/LICENCAS-TERCEIROS.md é reescrito com todos os blocos instalados.
Usa o HyperFrames do painel/pacote (node_modules/.bin/hyperframes) ou `npx hyperframes@0.7.111`.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "templates" / "blocos"
HF_VER = "0.7.111"
REG = "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry"
REPO = "https://github.com/heygen-com/hyperframes"
LICENCA = "Apache-2.0"

# nome -> (título PT, categoria, descrição PT)
BLOCOS = {
    "lt-clean-bar": ("Nome na tela — barra branca", "Lower third", "Cartão branco com faixa colorida: nome + função entram deslizando."),
    "lt-bold-block": ("Nome na tela — bloco forte", "Lower third", "Bloco escuro entra limpando a tela, nome em caixa alta."),
    "lt-kicker-name": ("Nome na tela — com etiqueta", "Lower third", "Etiqueta colorida em cima, nome grande e função embaixo."),
    "lt-mask-reveal": ("Nome na tela — revelação", "Lower third", "Uma faixa de cor atravessa e revela o nome."),
    "news-ticker": ("Faixa de notícias (ticker)", "Lower third", "Faixa estilo telejornal com selo AO VIVO, manchete e letreiro correndo."),
    "hw-write-title": ("Título escrito à mão", "Título", "O título é escrito com caneta na tela, traço a traço."),
    "yt-prism-title": ("Título prisma (YouTube)", "Título", "Título cinético com camadas coloridas, estilo abertura de canal."),
    "weight-wave": ("Título onda de peso", "Título", "As letras engordam e afinam em onda (fonte variável)."),
    "split-flap-board": ("Painel de aeroporto", "Título", "Letras viram como painel de embarque até formar a frase."),
    "mk-callout-highlight": ("Frase com destaque karaokê", "Legenda", "Frase em que as palavras acendem uma a uma, com destaque."),
    "mk-progress-stat": ("Número com barra de progresso", "Contador", "Número grande contando + rótulo + barra enchendo."),
    "mk-line-graph": ("Gráfico de linha", "Gráfico", "Uma ou duas linhas se desenham com pontos e valores."),
    "data-chart": ("Gráfico de barras e linha", "Gráfico", "Gráfico com barras subindo, linha e legenda."),
    "bar-chart-race": ("Corrida de barras", "Gráfico", "Barras ranqueadas crescem e se ultrapassam ao longo do tempo."),
    "mk-specs-list": ("Lista de itens (checklist)", "Lista", "Lista de características entrando linha a linha com check."),
    "editorial-flash-overlay": ("Flash editorial", "Transição", "Clarão rápido por cima — bom para trocar de cena."),
    "organic-light-leak-overlay": ("Vazamento de luz (filme)", "Transição", "Luz quente de filme passando por cima da cena."),
    "hw-scribble-transition": ("Transição rabisco", "Transição", "Rabiscos de caneta cobrem a tela e saem."),
    "mk-clone-wall-transition": ("Transição parede de palavras", "Transição", "Uma parede de palavras cobre a tela, inverte e revela a próxima cena."),
    "camcorder-hud": ("Filmadora (REC)", "Efeito", "Moldura de filmadora antiga: REC, bateria, data e contador."),
}


def hf_cmd():
    cands = [os.environ.get("HF_BIN", ""), str(ROOT / "node_modules" / ".bin" / "hyperframes.cmd"),
             str(ROOT.parent / "node_modules" / ".bin" / "hyperframes.cmd"),
             str(ROOT.parent.parent / "node_modules" / ".bin" / "hyperframes.cmd")]
    for c in cands:
        if c and Path(c).exists():
            return [c]
    return ["npx.cmd" if os.name == "nt" else "npx", "-y", f"hyperframes@{HF_VER}"]


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


_NAO_TEXTO = re.compile(r"[#{}\[\]()<>=/\\;:|@$`*_]|^\s|\s$|^(power|expo|sine|back|circ|elastic|steps|linear|ease)\b|\.(out|in|inOut)$|^(none|auto|center|left|right|top|bottom|middle|block|flex|hidden|visible|absolute|relative|bold|normal|start|end)$", re.I)


def textos_do_bloco(src: str, variables=None):
    """Textos visíveis trocáveis: nós de texto do HTML + strings de JS que parecem frase/palavra exibida.
    Textos que já são variáveis do bloco ficam de fora (o editor mostra a variável)."""
    var_defs = {" ".join(str(v.get("default", "")).split()) for v in variables or []}
    body = src.split("<body", 1)[-1]
    out = []
    html_sem = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S | re.I)
    for t in re.findall(r">([^<>]+)<", html_sem):
        t = " ".join(t.split())
        if len(t) >= 2 and re.search(r"[A-Za-zÀ-ú]", t):
            out.append(t)
    for sc in re.findall(r"<script\b[^>]*>(.*?)</script>", body, flags=re.S | re.I):
        sc = re.sub(r"(?m)^\s*//.*$", "", sc)
        for t in re.findall(r"""\b(?:title|text|headline|subtitle|label|caption|kicker|name)\s*:\s*["']([^"'\\\n]{2,90})["']""", sc):
            out.append(t)  # campos de CONFIG com nome de texto entram sempre
        for q, t in re.findall(r"""(["'])((?:(?!\1)[^\\\n]){2,90})\1""", sc):
            if not re.search(r"[A-Za-zÀ-ú]{2}", t) or _NAO_TEXTO.search(t) or '"' in t or "'" in t:
                continue
            if re.search(r"could not|fall(ing)? ?back|use strict|replaced with|highlight amount|shrink IS|HAMBURGEFONSTIV", t, re.I):
                continue
            if " " not in t and not re.match(r"^[A-ZÀ-Ú0-9]", t):  # palavra solta minúscula = nome técnico
                continue
            if re.match(r"^[A-Za-z]+(-[a-z0-9]+)+$", t) or re.match(r"^[a-z]+[A-Z]\w*$", t):  # kebab/camelCase
                continue
            if t in ("Inter", "Montserrat", "Error") or re.match(r"^(Libre|Barlow|Recursive|Caveat|Roboto|JetBrains)", t):
                continue
            out.append(t)
    vistos, res = set(), []
    for t in out:
        if t not in vistos and " ".join(t.split()) not in var_defs:
            vistos.add(t)
            res.append(t)
    return res[:16]


def importar(nome, tmp: Path, hf):
    info = get_json(f"{REG}/blocks/{nome}/registry-item.json")
    r = subprocess.run(hf + ["add", nome, "--dir", str(tmp), "--no-clipboard", "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:] or r.stdout[-400:])
    out = DEST / nome
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    files = []
    for f in info.get("files", []):
        src = tmp / f["target"]
        rel = f["target"]
        if f.get("type") == "hyperframes:composition":
            rel = f"{nome}.html"
        elif rel.startswith("compositions/"):
            rel = rel[len("compositions/"):]
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files.append(rel)
    tit, cat, desc = BLOCOS.get(nome, (info.get("title", nome), "Outros", info.get("description", "")))
    meta = {"name": nome, "titulo": tit, "categoria": cat, "descricao": desc,
            "title_en": info.get("title"), "description_en": info.get("description"),
            "duration": info.get("duration", 5), "width": (info.get("dimensions") or {}).get("width", 1920),
            "height": (info.get("dimensions") or {}).get("height", 1080), "tags": info.get("tags", []),
            "variables": info.get("variables", []), "files": files,
            "textos": textos_do_bloco((out / f"{nome}.html").read_text(encoding="utf-8"), info.get("variables")),
            "origem": f"{REPO}/tree/main/registry/blocks/{nome}", "licenca": LICENCA,
            "hyperframes": HF_VER}
    (out / "bloco.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def licencas():
    linhas = ["# Licenças de terceiros — Animações prontas (templates/blocos)", "",
              "Todos os blocos abaixo vêm do registry oficial do HyperFrames (HeyGen),",
              f"repositório {REPO} — licença **Apache-2.0** (texto completo em `LICENSE-APACHE-2.0.txt`).",
              "Arquivos originais copiados sem alteração; o editor só os adapta na hora de montar o vídeo.",
              "Fontes incluídas (.woff2) seguem a SIL Open Font License 1.1 (`OFL.txt` dentro do bloco).", "",
              "| Bloco | Título no painel | Origem | Licença | Arquivos extras |", "|---|---|---|---|---|"]
    for d in sorted(DEST.iterdir()):
        j = d / "bloco.json"
        if not j.exists():
            continue
        m = json.loads(j.read_text(encoding="utf-8"))
        extras = [f for f in m["files"] if not f.endswith(".html")]
        fontes = [f for f in extras if f.endswith((".woff2", ".ttf", ".otf"))]
        nota = ", ".join(extras) if extras else "—"
        if fontes:
            nota += " (fontes: OFL-1.1)"
        linhas.append(f"| `{m['name']}` | {m['titulo']} | {m['origem']} | {m['licenca']} | {nota} |")
    (DEST / "LICENCAS-TERCEIROS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    if sys.argv[1:2] == ["--textos"]:  # só recalcula a lista de textos trocáveis (sem baixar nada)
        for j in DEST.glob("*/bloco.json"):
            m = json.loads(j.read_text(encoding="utf-8"))
            m["textos"] = textos_do_bloco((j.parent / f"{m['name']}.html").read_text(encoding="utf-8"), m.get("variables"))
            j.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            print(m["name"], m["textos"])
        return
    nomes = sys.argv[1:] or list(BLOCOS)
    DEST.mkdir(parents=True, exist_ok=True)
    hf = hf_cmd()
    tmp = Path(tempfile.mkdtemp(prefix="hfblocos_"))
    (tmp / "hyperframes.json").write_text(json.dumps({"registry": REG, "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}), encoding="utf-8")
    try:
        for n in nomes:
            try:
                m = importar(n, tmp, hf)
                print("OK ", n, m["duration"], "s", len(m["variables"]), "variáveis")
            except Exception as e:
                print("ERRO", n, e)
        if not (DEST / "LICENSE-APACHE-2.0.txt").exists():
            with urllib.request.urlopen("https://raw.githubusercontent.com/heygen-com/hyperframes/main/LICENSE", timeout=30) as r:
                (DEST / "LICENSE-APACHE-2.0.txt").write_bytes(r.read())
        licencas()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
