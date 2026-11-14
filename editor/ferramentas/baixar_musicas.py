"""baixar_musicas.py — monta a biblioteca de músicas de fundo (recursos/musicas/).

Baixa faixas livres de Kevin MacLeod (incompetech.com, licença CC BY 4.0: pode usar em vídeo monetizado,
precisa citar o crédito na descrição). Tudo instrumental. Cada faixa é gravada uma vez e etiquetada com
os "climas" (suspense, terror, epico, triste, calmo, tecnologia, acao, leve) em recursos/musicas/catalogo.json,
que o escolhedor automático (editor/fabrica/lib/musica.py) usa.

Uso:  python editor/ferramentas/baixar_musicas.py        (pula o que já foi baixado)
"""
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "recursos" / "musicas"
BASE = "https://incompetech.com/music/royalty-free/"
UA = {"User-Agent": "Mozilla/5.0 (EstudioVideos painel local)"}

# título no catálogo da incompetech -> (climas, o que combina)
FAIXAS = {
    "SCP-x6x (Hopes)": (["suspense", "triste"], "mistério com violoncelo, narração de história"),
    "SCP-x5x (Outer Thoughts)": (["suspense"], "mistério leve, crime, enigmas"),
    "Stay the Course": (["suspense"], "tensão lenta, documentário investigativo"),
    "Man Down": (["suspense", "triste"], "tensão sombria, drama real"),
    "Intrepid": (["suspense"], "mistério antigo, história sombria"),
    "SCP-x2x (Unseen Presence)": (["terror"], "terror, presença sinistra"),
    "SCP-x1x (Gateway to Hell)": (["terror"], "terror pesado"),
    "Shadowlands 5 - Antechamber": (["terror", "suspense"], "ambiente tenso, assombrado"),
    "Shadowlands 1 - Horizon": (["terror", "triste"], "sombrio submerso"),
    "Rynos Theme": (["epico", "acao"], "épico, guerra, impérios"),
    "Undaunted": (["epico"], "tambores grandes, batalhas, história militar"),
    "Final Battle of the Dark Wizards": (["epico", "suspense"], "tensão que cresce, grandes conflitos"),
    "Tempting Secrets": (["epico", "suspense"], "segredos, conspirações, poder"),
    "Killers": (["epico", "acao"], "grandioso e intenso"),
    "Night Vigil": (["triste", "epico"], "lamento, tragédia, homenagem"),
    "Bittersweet": (["triste", "calmo"], "emocionante, nostálgico"),
    "Disquiet": (["triste", "suspense"], "inquietação suave"),
    "Lost Time": (["triste"], "perda, melancolia"),
    "Heavy Heart": (["triste"], "triste com esperança"),
    "Ether Vox": (["calmo"], "documentário calmo, natureza, curiosidades"),
    "Immersed": (["calmo", "tecnologia"], "minimalista, ciência"),
    "Floating Cities": (["calmo", "tecnologia"], "futuro, ciência, espaço"),
    "Late Night Radio": (["calmo"], "relaxado, histórias do dia a dia"),
    "Evening": (["calmo", "leve"], "leve e agradável"),
    "Brain Dance": (["tecnologia"], "tecnologia, mente, ciência"),
    "Rising Tide": (["tecnologia", "suspense"], "ritmo constante, negócios e tecnologia"),
    "Ethernight Club": (["tecnologia"], "eletrônico noturno, internet"),
    "Twisting": (["tecnologia", "suspense"], "ritmo de investigação"),
    "Hot Pursuit": (["acao"], "perseguição, esportes, ranking"),
    "Obliteration": (["acao"], "energia alta, guerra, esportes"),
    "Miami Nights - Extended Theme": (["acao", "leve"], "ritmo moderno, rankings"),
    "Death and Axes": (["acao", "epico"], "batalha, guerreiros"),
    "Newer Wave": (["leve", "tecnologia"], "otimista, ritmo anos 80"),
    "Pleasant Porridge": (["leve", "calmo"], "leve e simpático"),
    "Bleeping Demo": (["leve", "tecnologia"], "curiosidades, jogos"),
    "Cloud Dancer": (["leve", "acao"], "energia positiva, esportes"),
}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def secs(l):
    h, m, s = (int(x) for x in l.split(":"))
    return h * 3600 + m * 60 + s


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(BASE + "pieces.json", headers=UA)
    pecas = json.load(urllib.request.urlopen(req, timeout=60))
    por_titulo = {p["title"]: p for p in pecas}
    cat_f = DEST / "catalogo.json"
    cat = json.loads(cat_f.read_text(encoding="utf-8")) if cat_f.exists() else {}
    for titulo, (climas, uso) in FAIXAS.items():
        p = por_titulo.get(titulo)
        if not p:
            print("  (não achei no catálogo)", titulo)
            continue
        nome = slug(titulo) + ".mp3"
        f = DEST / nome
        if not f.exists() or f.stat().st_size < 100_000:
            url = BASE + "mp3-royaltyfree/" + urllib.parse.quote(p["filename"])
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                    f.write_bytes(r.read())
            except Exception as e:
                print("  FALHOU", titulo, type(e).__name__)
                continue
            print("  baixei", nome, f"{f.stat().st_size // 1024} KB")
        cat[nome] = {
            "titulo": titulo, "autor": "Kevin MacLeod (incompetech.com)", "licenca": "CC BY 4.0",
            "link": "https://incompetech.com/music/royalty-free/index.html?isrc=" + str(p.get("isrc") or ""),
            "licenca_link": "https://creativecommons.org/licenses/by/4.0/",
            "climas": climas, "uso": uso, "duracao": secs(p["length"]), "bpm": p.get("bpm"),
            "credito": f'Music: "{titulo}" by Kevin MacLeod (incompetech.com) — licensed under Creative Commons: By Attribution 4.0 (http://creativecommons.org/licenses/by/4.0/)',
        }
    cat_f.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(cat)} faixas em {DEST}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
