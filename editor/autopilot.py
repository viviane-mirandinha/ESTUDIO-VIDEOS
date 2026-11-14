"""Piloto automático do canal — fatia (a): rastrear + aprender.

Rastreia o canal do PRÓPRIO aluno (leitura pública, via yt-dlp, SEM login e SEM postar nada no YouTube),
mede as views de cada vídeo contra a MEDIANA do canal, marca os que estouraram (winner) e os que floparam,
e aprende um perfil do "que funciona" (palavras de título, faixa de duração, cadência de postagem, short×longo).

Tudo original e em PT-BR. Nada do Auto B-Roll Studio. Só a IDEIA de um tracker/learn.

Uso em linha de comando:
    python autopilot.py                      # rastreia o canal salvo e imprime o resumo
    python autopilot.py <url_do_canal>       # define o canal, rastreia e imprime
    python autopilot.py --status             # só lê o estado salvo (não busca nada)
    python autopilot.py --json               # imprime o estado em JSON
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path


def _ytdlp_exe():
    import shutil
    c = Path(sys.executable).parent / "yt-dlp.exe"
    return shutil.which("yt-dlp") or (str(c) if c.exists() else "yt-dlp")

ROOT = Path(__file__).resolve().parent
ESTADO = ROOT / "autopilot.json"          # estado do piloto (canal, último rastreio, perfil aprendido, histórico)

WINNER = 1.5      # ≥ 1,5× a mediana de views/hora → estourou
FLOP = 0.5        # ≤ 0,5× a mediana → floppou
NO_FLAGS = "CREATE_NO_WINDOW"

# Palavras vazias PT (não entram na contagem de "palavras que funcionam no título").
STOP = set("""a o os as um uma uns umas de do da dos das e em no na nos nas que com por para pra pro per
se sua seu suas seus meu minha nossos nosso ao à às aos ou mais menos muito pouco já não sim como quando
onde qual quais quem isso isto esse essa este esta aquele aquela entre sobre até sem após antes depois
é são foi era vai vou tem têm ser estar the of to in on for and""".split())


def _ler() -> dict:
    try:
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    except Exception:
        return {"canal": "", "videos": [], "aprendido": {}, "historico": [], "atualizado": 0}


def _salvar(st: dict):
    ESTADO.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def _canal_ok(url: str) -> bool:
    return bool(url) and "youtube.com" in url


def _url_videos(url: str) -> str:
    u = (url or "").strip().rstrip("/")
    if not re.search(r"/(videos|shorts|streams|featured)$", u):
        u += "/videos"
    return u


def buscar_videos(url: str, n: int = 30, timeout: int = 150) -> list[dict]:
    """Lista pública dos últimos vídeos do canal — SÓ --flat-playlist (não abre vídeo, não baixa, não loga).
    Devolve [{id, titulo, views, data(ts), dur}]. Data aproximada do youtubetab."""
    u = _url_videos(url)
    r = subprocess.run(
        [_ytdlp_exe(), "--no-warnings", "--flat-playlist", "--extractor-args", "youtubetab:approximate_date",
         "-I", f"1:{int(n)}", "--print", "%(id)s\t%(view_count)s\t%(timestamp)s\t%(duration)s\t%(title)s", u],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, creationflags=getattr(subprocess, NO_FLAGS, 0))
    vids = []
    for ln in r.stdout.splitlines():
        p = ln.split("\t", 4)
        if len(p) < 5:
            continue
        vid, views, ts, dur, tit = p
        try:
            views = int(views) if views.isdigit() else None
        except Exception:
            views = None
        try:
            ts = float(ts) if ts.split(".")[0].lstrip("-").isdigit() else None
        except Exception:
            ts = None
        try:
            dur = float(dur) if re.match(r"^\d+(\.\d+)?$", dur or "") else None
        except Exception:
            dur = None
        vids.append({"id": vid, "titulo": tit.strip(), "views": views, "data": ts, "dur": dur})
    return vids


def _mediana(xs: list[float]):
    s = sorted(x for x in xs if x is not None)
    if not s:
        return None
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def analisar(videos: list[dict], agora: float | None = None) -> dict:
    """Calcula views/hora de cada vídeo, a mediana do canal, a razão vs mediana e classifica
    winner/normal/flop. Usa views/hora (não views cru) pra não punir vídeo novo nem premiar só o antigo.
    Só entram na mediana vídeos com ≥ 12 h de vida (já tiveram chance)."""
    agora = agora or time.time()
    for v in videos:
        if v.get("views") is not None and v.get("data"):
            horas = max(12.0, (agora - v["data"]) / 3600.0)
            v["vph"] = v["views"] / horas
            v["idade_h"] = (agora - v["data"]) / 3600.0
            v["short"] = bool(v.get("dur") and v["dur"] <= 180)
        else:
            v["vph"] = None
            v["idade_h"] = None
            v["short"] = bool(v.get("dur") and v["dur"] <= 180)
    base = [v["vph"] for v in videos if v.get("vph") is not None and (v.get("idade_h") or 0) >= 12]
    med = _mediana(base)
    for v in videos:
        novo = (v.get("idade_h") or 99) < 12         # ainda não teve chance → não classifica como flop
        if v.get("vph") and med and not novo:
            v["razao"] = round(v["vph"] / med, 2)
            v["classe"] = "winner" if v["razao"] >= WINNER else ("flop" if v["razao"] <= FLOP else "normal")
        elif v.get("vph") and med and novo:
            v["razao"] = round(v["vph"] / med, 2)
            v["classe"] = "novo"
        else:
            v["razao"] = None
            v["classe"] = "novo" if novo else "sem_dados"
    return {"mediana_vph": med, "n": len(videos),
            "winners": sum(1 for v in videos if v.get("classe") == "winner"),
            "flops": sum(1 for v in videos if v.get("classe") == "flop")}


def _palavras(titulo: str) -> list[str]:
    ws = re.findall(r"[0-9a-zA-ZÀ-ÿ]{3,}", (titulo or "").lower())
    return [w for w in ws if w not in STOP and not w.isdigit()]


def _faixa_dur(seg: float | None) -> str:
    if not seg:
        return "?"
    if seg <= 60:
        return "ate 1min (short)"
    if seg <= 180:
        return "1-3min (short)"
    if seg <= 600:
        return "3-10min"
    if seg <= 1800:
        return "10-30min"
    return "mais de 30min"


def aprender(videos: list[dict]) -> dict:
    """Perfil do que funciona: tira o sinal dos WINNERS (e, se não houver, do terço de cima).
    Palavras de título mais comuns nos winners, faixa de duração campeã, cadência de postagem, short×longo."""
    com_razao = [v for v in videos if v.get("razao") is not None]
    winners = [v for v in videos if v.get("classe") == "winner"]
    if not winners and com_razao:
        com_razao.sort(key=lambda v: v["razao"], reverse=True)
        winners = com_razao[:max(1, len(com_razao) // 3)]

    freq: dict[str, int] = {}
    for v in winners:
        for w in set(_palavras(v["titulo"])):
            freq[w] = freq.get(w, 0) + 1
    palavras = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:12]

    faixas: dict[str, list[float]] = {}
    for v in winners:
        if v.get("dur"):
            faixas.setdefault(_faixa_dur(v["dur"]), []).append(v.get("vph") or 0)
    faixa_top = max(faixas.items(), key=lambda kv: _mediana(kv[1]) or 0)[0] if faixas else None

    datas = sorted(v["data"] for v in videos if v.get("data"))
    if len(datas) >= 2:
        gaps = [(b - a) / 86400.0 for a, b in zip(datas, datas[1:])]
        cadencia_dias = round(_mediana(gaps) or 0, 1) or None   # 0 = datas aproximadas iguais → sem info
    else:
        cadencia_dias = None

    n_short = sum(1 for v in videos if v.get("short"))
    n_long = sum(1 for v in videos if v.get("dur") and not v.get("short"))
    win_short = sum(1 for v in winners if v.get("short"))

    return {
        "palavras_titulo": [{"palavra": w, "winners": c} for w, c in palavras],
        "faixa_duracao_campea": faixa_top,
        "cadencia_dias": cadencia_dias,
        "short_vs_longo": {"shorts": n_short, "longos": n_long, "winners_short": win_short, "winners_total": len(winners)},
        "resumo": _resumo_texto(palavras, faixa_top, cadencia_dias, n_short, n_long, win_short, len(winners)),
    }


def _resumo_texto(palavras, faixa, cadencia, n_short, n_long, win_short, n_win) -> str:
    partes = []
    if palavras:
        partes.append("Títulos que estouraram usam muito: " + ", ".join(w for w, _ in palavras[:6]) + ".")
    if faixa:
        partes.append(f"A duração campeã é {faixa}.")
    if cadencia:
        partes.append(f"Você posta a cada ~{cadencia:g} dias.")
    if n_win:
        if win_short > n_win / 2:
            partes.append("Os winners são mais shorts — invista em short.")
        elif win_short == 0 and n_long:
            partes.append("Os winners são vídeos longos.")
    if not partes:
        partes.append("Ainda sem dados suficientes pra aprender — rastreie um canal com mais vídeos públicos.")
    return " ".join(partes)


def rastrear(url: str | None = None, n: int = 30) -> dict:
    """Busca → analisa → aprende → salva (com histórico de views pra acompanhar crescimento). Devolve o estado."""
    st = _ler()
    url = url or st.get("canal")
    if not _canal_ok(url):
        raise ValueError("Defina o link do seu canal do YouTube (ex.: https://youtube.com/@seucanal).")
    videos = buscar_videos(url, n=n)
    if not videos:
        raise RuntimeError("Não consegui ler os vídeos públicos desse canal (link certo? canal tem vídeos?).")
    stats = analisar(videos)
    perfil = aprender(videos)
    snap = {"t": time.time(), "mediana_vph": stats["mediana_vph"],
            "views": {v["id"]: v["views"] for v in videos if v.get("views") is not None}}
    hist = (st.get("historico") or [])[-30:] + [snap]       # guarda até 31 fotos pra ver crescimento
    st = {"canal": url, "videos": videos, "stats": stats, "aprendido": perfil,
          "historico": hist, "atualizado": time.time()}
    _salvar(st)
    return st


def definir_canal(url: str) -> dict:
    if not _canal_ok(url):
        raise ValueError("Link inválido — cole o link do canal do YouTube (começa com https:// e tem youtube.com).")
    st = _ler()
    st["canal"] = url.strip()
    _salvar(st)
    return st


def status() -> dict:
    return _ler()


# ===================== fatia (b): loop de 1 vídeo/dia (encadeia as peças do painel)
def _norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()


def escolher_assunto(videos: list[dict], usados=None):
    """Escolhe o melhor winner do nicho (fora_da_curva; senão o de maior vph) que ainda NÃO viramos vídeo.
    `usados` = títulos/temas já produzidos (evita repetir e segura a deriva de nicho)."""
    usados_n = [_norm(u) for u in (usados or []) if u]
    cand = [v for v in videos if v.get("fora_da_curva")] or [v for v in videos if v.get("vph")]
    cand = sorted(cand, key=lambda v: -(v.get("x_canal") or v.get("vph") or 0))
    for v in cand:
        tn = _norm(v.get("titulo"))
        if not tn:
            continue
        if any(u and (u in tn or tn in u) for u in usados_n):
            continue
        return v
    return cand[0] if cand else None


def plano_do_dia() -> dict:
    """Duração e regras sugeridas a partir do que o canal aprendeu na fatia (a). Vídeo faceless limpo por padrão."""
    ap = (_ler().get("aprendido") or {})
    faixa = ap.get("faixa_duracao_campea") or ""
    if "short" in faixa:
        dur = 60
    elif "3-10" in faixa:
        dur = 300
    elif "10-30" in faixa:
        dur = 600
    elif "30min" in faixa:
        dur = 900
    else:
        dur = 300
    return {"duracao": dur, "regras": {"broll_primeiro": True}}


def definir_config(d: dict) -> dict:
    st = _ler()
    for k in ("feed_id", "estilo", "voz", "canal_nome"):
        if d and k in d:
            st[k] = d[k]
    _salvar(st)
    return st


def registrar_producao(info: dict) -> dict:
    st = _ler()
    st["producoes"] = (st.get("producoes") or [])[-199:] + [info]
    _salvar(st)
    return st


def ja_feito_hoje() -> bool:
    hoje = time.strftime("%Y-%m-%d")
    return any(time.strftime("%Y-%m-%d", time.localtime(p.get("t", 0))) == hoje
               for p in (_ler().get("producoes") or []))


# ===================== fatia (d): "por que floppou" + import CSV do YouTube Studio
def _dur_seg(txt):
    """'0:03:12' ou '3:12' ou '192' → segundos."""
    s = str(txt or "").strip()
    if not s:
        return None
    if re.match(r"^\d+(\.\d+)?$", s):
        return float(s)
    partes = s.split(":")
    try:
        partes = [float(p) for p in partes]
    except Exception:
        return None
    seg = 0.0
    for p in partes:
        seg = seg * 60 + p
    return seg


def _num(txt):
    s = re.sub(r"[^\d,.\-]", "", str(txt or "")).replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def importar_csv(texto: str) -> dict:
    """Lê o CSV de 'Conteúdo' do YouTube Studio (impressões, CTR, retenção) e guarda por título.
    Colunas são achadas por aproximação do cabeçalho (serve PT e EN). Devolve {n, colunas}."""
    import csv as _csv
    import io
    linhas = list(_csv.reader(io.StringIO(texto)))
    if not linhas:
        raise ValueError("CSV vazio.")
    head = [h.strip().lower() for h in linhas[0]]

    def achar(*termos):
        for t in termos:               # prioridade: tenta cada termo na ordem (video title antes de content)
            for i, h in enumerate(head):
                if t in h:
                    return i
        return None
    ci = {
        "titulo": achar("video title", "título do víde", "titulo do vide", "título do conteúdo", "titulo", "título", "title", "conteúdo", "conteudo", "content"),
        "impressoes": achar("impress"),
        "ctr": achar("click-through", "clickthrough", "ctr", "taxa de cliques", "cliques de impress"),
        "views": achar("views", "visualiza"),
        "ret_seg": achar("average view duration", "duração média", "duracao media"),
        "ret_pct": achar("average percentage viewed", "porcentagem média", "porcentagem media", "% médio", "média assistida"),
    }
    if ci["titulo"] is None:
        raise ValueError("Não achei a coluna de título no CSV (exporte a tabela 'Conteúdo' do YouTube Studio).")
    dados = {}
    for row in linhas[1:]:
        if len(row) <= ci["titulo"]:
            continue
        tit = (row[ci["titulo"]] or "").strip()
        if not tit or tit.lower() in ("total", "totais"):
            continue
        g = lambda k: row[ci[k]] if (ci[k] is not None and ci[k] < len(row)) else None
        dados[_norm(tit)] = {
            "titulo": tit,
            "impressoes": _num(g("impressoes")),
            "ctr": _num(g("ctr")),
            "views": _num(g("views")),
            "retencao_seg": _dur_seg(g("ret_seg")),
            "retencao_pct": _num(g("ret_pct")),
        }
    st = _ler()
    st["csv"] = {"quando": time.time(), "metrica": dados,
                 "colunas": [k for k, v in ci.items() if v is not None]}
    _salvar(st)
    return {"n": len(dados), "colunas": st["csv"]["colunas"]}


def _csv_do_video(titulo):
    csv = (_ler().get("csv") or {}).get("metrica") or {}
    tn = _norm(titulo)
    if tn in csv:
        return csv[tn]
    for k, v in csv.items():       # casamento aproximado (título cortado no Studio)
        if k and (k in tn or tn in k):
            return v
    return None


def sinais_flop(video: dict) -> dict:
    """Monta os sinais do diagnóstico de UM vídeo do canal (da tabela da fatia a), cruzando com o
    perfil aprendido e, se houver, o CSV do Studio. Só números — a explicação honesta vem depois (Ollama)."""
    st = _ler()
    ap = st.get("aprendido") or {}
    palavras = [w["palavra"] for w in (ap.get("palavras_titulo") or [])]
    tit = video.get("titulo") or ""
    tn = _norm(tit)
    usa_palavra = [w for w in palavras if w and w in tn]
    faixa_campea = ap.get("faixa_duracao_campea")
    dur = video.get("dur")
    s = {
        "titulo": tit,
        "classe": video.get("classe"),
        "razao_vs_mediana": video.get("razao"),
        "vph": round(video.get("vph"), 1) if video.get("vph") else None,
        "titulo_chars": len(tit),
        "titulo_usa_palavra_winner": usa_palavra,
        "faixa_campea": faixa_campea,
        "este_short": bool(video.get("short")),
        "tem_csv": False,
    }
    csv = _csv_do_video(tit)
    if csv:
        s["tem_csv"] = True
        s["impressoes"] = csv.get("impressoes")
        s["ctr"] = csv.get("ctr")
        s["retencao_seg"] = csv.get("retencao_seg")
        s["retencao_pct"] = csv.get("retencao_pct")
        s["ctr_baixo"] = (csv.get("ctr") is not None and csv.get("ctr") < 3)
        s["retencao_baixa"] = (csv.get("retencao_pct") is not None and csv.get("retencao_pct") < 30)
        s["poucas_impressoes"] = (csv.get("impressoes") is not None and csv.get("impressoes") < 500)
    return s


def _print_resumo(st: dict):
    print(f"Canal: {st.get('canal') or '—'}")
    stats = st.get("stats") or {}
    med = stats.get("mediana_vph")
    print(f"Vídeos lidos: {stats.get('n', 0)} · mediana {med:.1f} views/h · winners {stats.get('winners', 0)} · flops {stats.get('flops', 0)}"
          if med else "Sem estatística ainda.")
    print("\nTop 10 por views/hora:")
    vs = sorted((st.get("videos") or []), key=lambda v: v.get("vph") or -1, reverse=True)[:10]
    for v in vs:
        tag = {"winner": "🚀", "flop": "💤", "normal": "•", "novo": "🆕"}.get(v.get("classe"), "·")
        r = f"{v['razao']:.2f}×" if v.get("razao") else "—"
        print(f"  {tag} {r:>6}  {(v.get('views') or 0):>8} views  {v['titulo'][:60]}")
    ap = st.get("aprendido") or {}
    print("\nO que funciona:\n  " + (ap.get("resumo") or "—"))


def main(argv):
    if "--status" in argv:
        _print_resumo(_ler())
        return
    if "--json" in argv:
        print(json.dumps(_ler(), ensure_ascii=False, indent=1))
        return
    url = next((a for a in argv[1:] if a.startswith("http")), None)
    if url:
        definir_canal(url)
    st = rastrear(url)
    _print_resumo(st)


if __name__ == "__main__":
    main(sys.argv)
