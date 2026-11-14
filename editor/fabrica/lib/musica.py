"""musica.py — música de fundo dos vídeos: escolha automática, preparo e volume seguro.

Três modos (escolhidos na hora de pedir o vídeo):
  nenhuma  → nada é adicionado
  auto     → escolhe sozinho na biblioteca (recursos/musicas/catalogo.json) pelo assunto, roteiro e estilo
  minha    → usa o arquivo de áudio que a pessoa enviou

Em qualquer modo com música, o arquivo é NORMALIZADO (mesma altura em todas as faixas, mesmo a da própria
pessoa) e entra com volume calculado em relação à voz — por isso nenhuma música "cobre" o narrador:
  baixa    → bem baixinha (≈ 18 dB abaixo da voz), sempre abaixa mais quando o narrador fala
  presente → se faz notar (≈ 11 dB abaixo da voz); com "abaixar quando o narrador fala" ligado (padrão) cai
             mais ~10 dB enquanto ele fala. Sem isso, o volume é limitado automaticamente.
O crédito (CC BY) vai para <pasta>/musica-credito.txt.
"""
import json
import random
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BIB = ROOT / "recursos" / "musicas"
CAT = BIB / "catalogo.json"
USADAS = BIB / ".usadas.json"

# volumes (a faixa já sai normalizada em ~ -16 LUFS, igual à voz)
VOLUME = {"baixa": 0.12, "presente": 0.28}
VOLUME_PRESENTE_SEM_DUCK = 0.20   # sem abaixar quando fala, "presente" é limitado pra nunca cobrir o narrador
NORMALIZA_LUFS = -16

# palavras do tema/roteiro → clima (peso). O texto é passado sem acento e em minúsculas.
PALAVRAS = {
    "terror": "terror assombr fantasma maldic demonio sobrenatural creepy medo pavor possuid paranormal horror morto cemiterio macabr sinistr",
    "suspense": "misterio mistério crime assassin serial investig desapare segredo conspira enigma caso misterios culto sequestr golpe fraude espion psicolog sombri perturb manipul obsess criminos trafic",
    "epico": "guerra batalha imperio imperador roma romano coliseu gladiador exercito soldado viking espartan medieval cavale rei rainha conquist legiao napoleao egito faraoh antigo antiga civilizacao dinastia mitolog heroi lenda",
    "triste": "morte tragedia luto perda sofr solidao depress abandon vitima doenca peste fome holocausto acidente desastre naufragio saudade historia triste emocion",
    "calmo": "natureza animal oceano planeta cosmos universo espaco historia curiosidade documentario relax sono dormir meditac fato cientific biologia",
    "tecnologia": "tecnologia inteligencia artificial ia robo computador internet startup empresa negocio dinheiro financ bitcoin cripto celular app maquina futuro ciencia fisica quimica engenharia dados algoritmo",
    "acao": "futebol esporte jogo campeonato copa corrida velocidade ranking top gol atleta luta mma boxe carro formula guerra tank arma",
    "leve": "engracad divertid curiosidade fato comida receita viagem cidade animal fofo dica truque hack motivac superac sucesso feliz",
}

# estilo da fábrica → clima(s) padrão (empurra a escolha quando o texto não diz muito)
ESTILO_CLIMA = {
    "psicologia-sombria": ["suspense", "triste"], "reddit-story": ["suspense", "leve"], "historia-simples": ["epico", "calmo"],
    "documentario-noturno": ["suspense", "calmo"], "short-documentario": ["suspense", "calmo"], "broll-documentario": ["calmo", "suspense"],
    "stickman": ["leve", "acao"],
}

CLIMA_NOME = {"terror": "terror", "suspense": "suspense/mistério", "epico": "épico/histórico", "triste": "dramático/triste",
              "calmo": "calmo/documentário", "tecnologia": "tecnologia/ciência", "acao": "ação/esporte", "leve": "leve/curiosidade"}


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s)


def catalogo():
    try:
        d = json.loads(CAT.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {k: v for k, v in d.items() if (BIB / k).exists()}


def pontuar(texto, estilo=""):
    """{clima: pontos} pelo assunto (tema + roteiro) e pelo estilo."""
    t = _norm(texto)
    pts = {c: 0.0 for c in PALAVRAS}
    for c, ws in PALAVRAS.items():
        for w in set(_norm(ws).split()):
            n = t.count(w)
            if n:
                pts[c] += min(n, 6) * (2.0 if len(w) >= 6 else 1.0)
    for i, c in enumerate(ESTILO_CLIMA.get(estilo, [])):
        pts[c] += 4.0 if i == 0 else 2.0
    return pts


def _recentes():
    try:
        return json.loads(USADAS.read_text(encoding="utf-8"))[-8:]
    except Exception:
        return []


def _marcar(nome):
    try:
        USADAS.write_text(json.dumps((_recentes() + [nome])[-12:]), encoding="utf-8")
    except Exception:
        pass


def escolher(texto, estilo="", duracao=0, marcar=False):
    """Melhor faixa da biblioteca pro assunto. Devolve {arquivo, titulo, climas, motivo, ...} ou None (biblioteca vazia).
    Evita repetir as últimas faixas usadas, pra vídeos seguidos não ficarem com a mesma música."""
    cat = catalogo()
    if not cat:
        return None
    pts = pontuar(texto, estilo)
    if max(pts.values()) <= 0:
        pts["calmo"] = 1.0   # sem pista nenhuma: música neutra de documentário
    rec = _recentes()
    pont = []
    for nome, info in cat.items():
        s = sum(pts.get(c, 0) * (1.0 if i == 0 else 0.6) for i, c in enumerate(info.get("climas", [])))
        if nome in rec:
            s *= 0.55 if rec[::-1].index(nome) > 2 else 0.3
        pont.append((s, nome))
    pont.sort(reverse=True)
    topo = [p for p in pont if p[0] >= pont[0][0] * 0.85][:3]   # empate técnico → sorteia entre os melhores
    s, nome = random.choice(topo)
    info = cat[nome]
    clima = max(info.get("climas", ["calmo"]), key=lambda c: pts.get(c, 0))
    motivo = f"{CLIMA_NOME.get(clima, clima)}" + (f" — {info['uso']}" if info.get("uso") else "")
    if marcar:
        _marcar(nome)
    return {"arquivo": nome, "caminho": str(BIB / nome), "titulo": info["titulo"], "motivo": motivo, "clima": clima,
            "credito": info.get("credito", ""), "duracao": info.get("duracao")}


def volume(nivel, duck=True):
    v = VOLUME.get(nivel, VOLUME["baixa"])
    if nivel == "presente" and not duck:
        v = min(v, VOLUME_PRESENTE_SEM_DUCK)
    return v


def config_audio(src, nivel="baixa", duck=True, start=0):
    """Bloco edit["audio"]["music"] (o build_from_edit.py faz o resto: loop, fade, sidechain)."""
    nivel = nivel if nivel in VOLUME else "baixa"
    duck = True if nivel == "baixa" else bool(duck)   # "baixinha" sempre abaixa mais quando fala
    return {"src": src, "volume": volume(nivel, duck), "start": start, "fade_out": 2.0, "duck": duck,
            "duck_ratio": 10 if nivel == "presente" else 6, "nivel": nivel}


def _normalizar(origem: Path, destino: Path):
    """Deixa a faixa na altura padrão (loudnorm 1 passada) e em mp3. Se o ffmpeg falhar, copia como está."""
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(origem), "-vn", "-af", f"loudnorm=I={NORMALIZA_LUFS}:TP=-2:LRA=11",
                            "-ar", "48000", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k", str(destino)],
                           capture_output=True, text=True, timeout=600)
        if r.returncode == 0 and destino.exists() and destino.stat().st_size > 10_000:
            return True
    except Exception:
        pass
    shutil.copy2(origem, destino.with_suffix(origem.suffix.lower()))
    return False


def preparar(pasta, modo, texto="", estilo="", nivel="baixa", duck=True, arquivo=None, duracao=0):
    """Põe a música dentro da pasta do vídeo. Devolve {"music": {...}, "titulo", "credito", "motivo"} ou None (modo nenhuma / erro).
    modo = "auto" | "minha" (arquivo = caminho do áudio da pessoa)."""
    pasta = Path(pasta)
    if modo == "minha":
        if not arquivo or not Path(arquivo).exists():
            return None
        origem, info = Path(arquivo), {"titulo": Path(arquivo).stem, "motivo": "a música que você escolheu", "credito": ""}
    elif modo == "auto":
        e = escolher(texto, estilo, duracao, marcar=True)
        if not e:
            return None
        origem, info = Path(e["caminho"]), e
    else:
        return None
    pasta.mkdir(parents=True, exist_ok=True)
    dst = pasta / "musica.mp3"
    for velho in pasta.glob("musica.*"):
        if velho.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".opus"):
            velho.unlink(missing_ok=True)
    if not _normalizar(origem, dst):
        dst = next(pasta.glob("musica.*"), dst)
    if not dst.exists():
        return None
    if info.get("credito"):
        (pasta / "musica-credito.txt").write_text(
            "Cole isto na descrição do vídeo (a licença CC BY exige o crédito):\n\n" + info["credito"] + "\n", encoding="utf-8")
    return {"music": config_audio(dst.name, nivel, duck), "titulo": info.get("titulo", ""), "motivo": info.get("motivo", ""),
            "credito": info.get("credito", ""), "arquivo": dst.name}
