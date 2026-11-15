# emalta.py — "🔥 Bombando": vídeos faceless em alta AGORA (views/hora), coletados por nós com yt-dlp sem baixar vídeo.
# Fontes: (1) busca do YouTube por palavras de nichos faceless (EN/ES/PT), ordenada por views na última semana;
#         (2) página /videos dos canais de referência do catálogo (ESTILOS-NOVOS/*/REFERENCIA.txt).
# Só --flat-playlist + approximate_date (lê a listagem, não abre vídeo). Resultado em EDITOR VIDEOS/.cache/bombando.json.
import json
import re
import subprocess
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

from . import rede_yt

ROOT =Path(__file__).resolve().parent.parent.parent          # EDITOR VIDEOS
CACHE = ROOT / ".cache" / "bombando.json"
SP_SEMANA_VIEWS = "CAMSAggD"     # filtro do YouTube: enviados esta semana, ordenados por visualizações
JANELA_H = 7 * 24                # só entra vídeo com até 7 dias
MIN_H = 2                        # idade mínima para o views/hora não explodir

# nicho -> idioma -> buscas (palavras típicas de canais sem rosto)
NICHOS = {
    "História": {"EN": ["dark history documentary"], "ES": ["historia oscura documental"], "PT": ["história sombria documentário"]},
    "Mistério e terror": {"EN": ["unsolved mysteries explained", "scary true stories"], "ES": ["misterios sin resolver", "historias de terror reales"],
                          "PT": ["mistérios não resolvidos", "histórias de terror reais"]},
    "Curiosidades": {"EN": ["facts you didn't know"], "ES": ["curiosidades que no sabías"], "PT": ["curiosidades que você não sabia"]},
    "Psicologia": {"EN": ["dark psychology"], "ES": ["psicología oscura"], "PT": ["psicologia sombria"]},
    "Dinheiro": {"EN": ["how the rich get richer explained"], "ES": ["finanzas personales explicado"], "PT": ["como ficar rico explicado"]},
    "Histórias (Reddit)": {"EN": ["reddit stories"], "ES": ["historias de reddit"], "PT": ["histórias do reddit"]},
    "Tecnologia e IA": {"EN": ["ai news explained"], "ES": ["inteligencia artificial noticias"], "PT": ["inteligência artificial notícias"]},
    "Fé e religião": {"EN": ["bible stories explained"], "ES": ["historias de la biblia"], "PT": ["histórias da bíblia"]},
    "Esportes": {"EN": ["football documentary"], "ES": ["futbol documental"], "PT": ["futebol documentário"]},
}
# canais de TV/jornal/marca não são "sem rosto" — ficam de fora
NAO_FACELESS = re.compile(r"\b(news|noticias|notícias|noticiero|jornal|tv|official|oficial|bbc|cnn|cbc|fox|nbc|abc|cbs|espn|sky|globo|record|televisa|univision|telemundo|reuters|bloomberg)\b", re.I)
CAMPOS = "%(id)s\t%(title)s\t%(channel)s\t%(channel_url)s\t%(uploader_url)s\t%(view_count)s\t%(timestamp)s\t%(duration)s"
_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _ytdlp(url, limite=20):
    r = subprocess.run([*rede_yt.cmd(),"--no-warnings", "--flat-playlist", "--extractor-args", "youtubetab:approximate_date",
                        "-I", f"1:{limite}", "--print", CAMPOS, url], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=150, creationflags=_NOWIN)
    out = []
    for ln in r.stdout.splitlines():
        p = ln.split("\t")
        if len(p) < 8 or not re.match(r"^[\w-]{11}$", p[0]):
            continue
        out.append(dict(zip(("id", "titulo", "canal", "canal_url", "uploader_url", "views", "ts", "dur"), p)))
    return out


_PT = set("não nao você voce uma são sao pelo pela isso também tambem ele ela seu sua mais foi com para os as dos das em um ao aos há ja já muito como quando porque era fez tinha nunca todos mesmo história histórias historias reais ninguém segredo".split())
_ES = set("no que el los las una es con para por del su sus más mas fue esto también tambien ella pero muy como cuando porque era hizo tenía nunca todos mismo historias reales nadie cómo qué secreto lo se al un y".split())
_EN = set("the of and to in is for on with you your how why what this that was are his her they their from an it be not about".split())


def idioma_titulo(t, padrao):
    """Idioma pelo título (PT/ES/EN). Em dúvida, devolve o padrão (idioma da busca)."""
    t = (t or "").lower()
    pt = 2 * len(re.findall(r"[ãõç]", t)); es = 2 * len(re.findall(r"[ñ¿¡]", t)); en = 0
    for w in re.findall(r"[a-záéíóúâêôãõçñü]+", t):
        pt += w in _PT and w not in _ES
        es += w in _ES and w not in _PT
        en += w in _EN
    # palavras comuns às duas (como, historia, que...) não pontuam; precisa vencer com folga
    melhor = max((pt, "PT"), (es, "ES"), (en, "EN"))
    seg = sorted((pt, es, en), reverse=True)[1]
    return melhor[1] if melhor[0] >= 2 and melhor[0] > seg else padrao


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _item(x, idioma, nicho, origem, agora):
    views, ts = _num(x["views"]), _num(x["ts"])
    if views is None or ts is None:
        return None
    horas = (agora - ts) / 3600
    if horas > JANELA_H or horas < 0:
        return None
    dur = _num(x["dur"])
    idioma = idioma_titulo(x["titulo"], idioma)
    canal_url = x["canal_url"] if x["canal_url"] not in ("NA", "") else x["uploader_url"]
    return {"id": x["id"], "titulo": x["titulo"], "canal": x["canal"] if x["canal"] != "NA" else "",
            "canal_url": canal_url if canal_url != "NA" else "", "url": f"https://www.youtube.com/watch?v={x['id']}",
            "thumb": f"https://i.ytimg.com/vi/{x['id']}/mqdefault.jpg", "views": int(views), "horas": round(horas, 1),
            "vph": int(views / max(MIN_H, horas)), "duracao": int(dur) if dur else None,
            "formato": "short" if dur and dur <= 70 else "longo", "idioma": idioma, "nicho": nicho, "origem": origem}


def canais_catalogo(estilos_novos: Path, maximo=40):
    """Canais de referência do catálogo: linhas '## Nome [EN] — https://www.youtube.com/@canal' dos REFERENCIA.txt."""
    vistos, out = set(), []
    if not estilos_novos or not Path(estilos_novos).exists():
        return out
    for f in sorted(Path(estilos_novos).glob("*/REFERENCIA.txt")):
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r"(?m)^##\s*(.+?)\s*\[(\w+)\]\s*[—–-]+\s*(https://www\.youtube\.com/[^\s|]+)", txt):
            u = m.group(3).rstrip("/")
            if u not in vistos:
                vistos.add(u)
                out.append({"canal": m.group(1).strip(), "idioma": m.group(2).upper()[:2], "url": u,
                            "estilo": re.sub(r"^\d+-", "", f.parent.name).replace("-", " ")})
    return out[:maximo]


def coletar(prog=None, estilos_novos=None, pausa=2.0):
    """Roda as buscas + canais e grava .cache/bombando.json. prog(pct, msg) opcional."""
    agora = time.time()
    tarefas = []
    for nicho, por_idioma in NICHOS.items():
        for idioma, buscas in por_idioma.items():
            for q in buscas:
                tarefas.append(("busca", q, idioma, nicho, ""))
    for c in canais_catalogo(estilos_novos):
        tarefas.append(("canal", c["url"], c["idioma"], "Canais do catálogo", c["canal"]))
    itens, erros = {}, 0
    for k, (tipo, alvo, idioma, nicho, nome_canal) in enumerate(tarefas):
        if prog:
            prog(100 * k / max(1, len(tarefas)), f"{'Buscando' if tipo == 'busca' else 'Lendo canal'} {k + 1} de {len(tarefas)}: {alvo[-40:]}")
        try:
            if tipo == "busca":
                url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": alvo, "sp": SP_SEMANA_VIEWS})
                lst = _ytdlp(url, 20)
            else:
                lst = _ytdlp(alvo + ("" if re.search(r"/(videos|shorts)$", alvo) else "/videos"), 8)
        except Exception:
            erros += 1
            lst = []
        for x in lst:
            it = _item(x, idioma, nicho, tipo, agora)
            if it and tipo == "canal":
                it["canal"] = it["canal"] or nome_canal
                it["canal_url"] = it["canal_url"] or alvo
            if it and NAO_FACELESS.search(it["canal"] or ""):
                continue
            if it and (it["id"] not in itens or itens[it["id"]]["origem"] == "canal"):
                itens[it["id"]] = it
        time.sleep(pausa)   # devagar de propósito (evita bot-check do YouTube)
    if not itens and erros:   # tudo falhou: não sobrescreve a lista antiga e avisa em vez de dizer "atualizada"
        raise RuntimeError(f"A busca falhou nas {erros} tentativas (yt-dlp não rodou ou sem internet). A lista anterior foi mantida.")
    lista = sorted(itens.values(), key=lambda x: -x["vph"])
    d = {"atualizado": datetime.now().strftime("%d/%m/%Y %H:%M"), "ts": agora, "total": len(lista), "erros": erros,
         "nichos": list(NICHOS) + ["Canais do catálogo"], "itens": lista}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return {"videos": len(lista), "buscas": len(tarefas), "erros": erros}


def ler():
    if CACHE.exists():
        try:
            d = json.loads(CACHE.read_text(encoding="utf-8"))
            for it in d.get("itens", []):   # conserta etiquetas de listas antigas
                it["idioma"] = idioma_titulo(it.get("titulo"), it.get("idioma"))
            return d
        except Exception:
            pass
    return {"atualizado": "", "itens": [], "nichos": list(NICHOS) + ["Canais do catálogo"], "vazio": True}



# ------------------------------------------------------------------ 📊 ranking por nicho (aba "Estilos em alta")
# O que cada nicho pede e quais peças combinam — escrito por nós, em palavras simples. "dificil" = dá mais trabalho
# (pesquisa e imagem certa pra cada frase), mesmo quando paga bem.
NICHO_INFO = {
    "História": {"pede": ["Fatos com data e lugar certos", "Imagens antigas reais (mapas, pinturas, fotos de época)", "Narração calma, tipo documentário"],
                 "pecas": ["titulo", "numero", "etiqueta", "credito"], "estilo": "historia-simples", "dificil": True},
    "Mistério e terror": {"pede": ["Gancho forte nos primeiros 10 segundos", "Clima escuro e música tensa", "Detalhes reais (datas, nomes, lugares)"],
                          "pecas": ["titulo", "numero", "etiqueta"], "estilo": "documentario-noturno", "dificil": False},
    "Curiosidades": {"pede": ["Vários fatos curtos e rápidos", "Uma imagem certinha pra cada fato", "Números grandes na tela"],
                     "pecas": ["titulo", "numero", "credito"], "estilo": "broll-documentario", "dificil": False},
    "Psicologia": {"pede": ["Frases de impacto na legenda", "Imagens simbólicas (sombra, mente, pessoas)", "Ritmo mais lento, reflexivo"],
                   "pecas": ["titulo", "legenda"], "estilo": "psicologia-sombria", "dificil": False},
    "Dinheiro": {"pede": ["Números e valores aparecendo quando fala", "Exemplos do dia a dia", "Comparações (antes × depois)"],
                 "pecas": ["titulo", "numero", "etiqueta"], "estilo": "broll-documentario", "dificil": False},
    "Histórias (Reddit)": {"pede": ["Narração envolvente do começo ao fim", "Legenda grande e fácil de ler", "Fundo simples que não distrai"],
                           "pecas": ["legenda", "titulo"], "estilo": "reddit-story", "pedido": True, "dificil": False},
    "Tecnologia e IA": {"pede": ["Notícia nova (de esta semana)", "Telas, logos de produto e gráficos", "Explicar fácil, sem termo difícil"],
                        "pecas": ["titulo", "numero", "credito"], "estilo": "broll-documentario", "dificil": True},
    "Fé e religião": {"pede": ["Voz calma e acolhedora", "Imagens bonitas (céu, luz, pinturas)", "Versículo ou frase na tela"],
                      "pecas": ["titulo", "legenda"], "estilo": "historia-simples", "dificil": False},
    "Esportes": {"pede": ["Lances e nomes de jogadores certos", "Números (gols, títulos, valores)", "Ritmo rápido, empolgante"],
                 "pecas": ["titulo", "numero", "etiqueta"], "estilo": "broll-documentario", "dificil": True},
}
SELOS = {
    "alta": ("🔥 Em alta", "Os vídeos desse nicho estão ganhando bem mais views por hora que a média."),
    "subindo": ("📈 Subindo", "Muitos vídeos novos (menos de 2 dias) já indo bem — o nicho está esquentando."),
    "estavel": ("➖ Estável", "Views normais e constantes. Bom pra postar sempre."),
    "dificil": ("⚠ Difícil", "Paga bem, mas dá mais trabalho: precisa de pesquisa e da imagem certa pra cada frase."),
}


def _mediana(a):
    a = sorted(a)
    return a[len(a) // 2] if a else 0


def ranking_nichos(formato="longo"):
    """Um cartão por nicho: selo, views/hora típica, o que pede, peças que combinam, estilo nosso recomendado e os vídeos que puxam."""
    d = ler()
    itens = [x for x in d.get("itens") or [] if x.get("formato") == formato and x.get("nicho") in NICHO_INFO]
    por_nicho = {n: sorted([x["vph"] for x in itens if x["nicho"] == n], reverse=True)[:10] for n in NICHO_INFO}
    geral = _mediana([_mediana(v) for v in por_nicho.values() if v]) or 1   # "média" = nicho do meio da tabela
    out = []
    for nicho, info in NICHO_INFO.items():
        L = sorted([x for x in itens if x["nicho"] == nicho], key=lambda x: -x["vph"])
        if not L:
            continue
        top = L[:10]
        vph = _mediana([x["vph"] for x in top])
        novos = sum(1 for x in top if x["horas"] <= 48) / len(top)
        if vph >= geral * 1.6:
            selo = "alta"
        elif info.get("dificil"):
            selo = "dificil"
        elif novos >= 0.4 and vph >= geral * 0.9:
            selo = "subindo"
        else:
            selo = "estavel"
        out.append({"nicho": nicho, "selo": selo, "selo_nome": SELOS[selo][0], "selo_dica": SELOS[selo][1], "vph": int(vph),
                    "x_media": round(vph / geral, 1), "videos": len(L), "pede": info["pede"], "pecas": info["pecas"],
                    "estilo": info["estilo"], "pedido": bool(info.get("pedido")), "dificil": bool(info.get("dificil")),
                    "exemplos": [{k: x[k] for k in ("titulo", "canal", "url", "thumb", "vph", "views", "horas", "idioma")} for x in L[:4]]})
    ordem = {"alta": 0, "subindo": 1, "estavel": 2, "dificil": 3}
    out.sort(key=lambda n: (ordem[n["selo"]], -n["vph"]))
    return {"atualizado": d.get("atualizado") or "", "formato": formato, "nichos": out}


if __name__ == "__main__":   # teste: python -m lib.emalta (dentro de fabrica)
    import sys
    print(coletar(lambda p, m: print(f"{p:5.1f}% {m}"), Path(sys.argv[1]) if len(sys.argv) > 1 else None))
