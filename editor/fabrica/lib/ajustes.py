# ajustes.py — configurações do Estúdio (EDITOR VIDEOS\ajustes.json), lidas pelo painel e pela fábrica.
import json
from pathlib import Path

EDITOR = Path(__file__).resolve().parent.parent.parent      # EDITOR VIDEOS
ARQ = EDITOR / "ajustes.json"
ENV_ARQ = EDITOR.parent / ".env"                              # chaves de API (nunca sobem pro GitHub — está no .gitignore)

PADRAO = {
    "gemini_key": "",
    "elevenlabs_key": "",
    "serper_key": "",
    "youtube_key": "",
    "europeana_key": "",
    "vimeo_token": "",
    "serpapi_key": "",
    "hf_token": "",
    "fish_key": "",
    "fish_modelo": "drama-3",                 # modelo do Fish Audio no cabeçalho "model": drama-3 | s2.1-pro | s2-pro | s1 (s1 será desligado em 31/12/2026)
    "fish_vozes": [],                       # ids de vozes do Fish que você quer sempre na lista (a "Adam" etc.)
    "modelo_ollama": "qwen2.5:7b",            # padrão leve (pacote dos alunos); neste PC o ajustes.json usa mistral-small3.1 (melhor português)
    "voz": "edge:pt-BR-ThalitaMultilingualNeural",        # motor:nome  (edge | fish | qwen3 | chatterbox | auto)
    # migração C→D (23/10): pasta real no D:, o Desktop ficou só com atalho
    "pasta_saida": next((d for d in (str(__import__("pathlib").Path(__file__).resolve().parents[3] / "VIDEOS"),) if Path(d).exists()),
                        str(__import__("pathlib").Path(__file__).resolve().parents[3] / "VIDEOS")),
    "pexels_key": "",
    "pixabay_key": "",
    "anthropic_key": "",                      # opcional: revisar roteiro com o Claude (gasta tokens)
    "idioma": "pt-BR",
    "ollama_url": "",                         # Ollama em outro PC (Tailscale), ex.: http://100.x.x.x:11434 — vazio = o deste PC
    "vs_remoto_url": "",                      # VoiceStudio em outro PC (Tailscale), ex.: http://100.x.x.x:3900 — voz pela placa de vídeo de lá
    "modelo_claude": "sonnet",                # modelo do Claude Code nos pedidos: sonnet (mais novo) | opus (mais novo) | haiku | nome completo
}

IDIOMAS = {
    "pt-BR": {"nome": "Português (Brasil)", "llm": "português do Brasil", "whisper": "pt"},
    "en-US": {"nome": "Inglês (EUA)", "llm": "American English", "whisper": "en"},
    "es-MX": {"nome": "Espanhol (México)", "llm": "español de México", "whisper": "es"},
}


# chave do Ajustes → variável que scripts/skills/Claude leem
ENV_CHAVES = {"gemini_key": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], "pexels_key": ["PEXELS_API_KEY"], "pixabay_key": ["PIXABAY_KEY", "PIXABAY_API_KEY"],
              "elevenlabs_key": ["ELEVENLABS_API_KEY"], "serper_key": ["SERPER_API_KEY"], "youtube_key": ["YOUTUBE_API_KEY"],
              "europeana_key": ["EUROPEANA_API_KEY"], "vimeo_token": ["VIMEO_ACCESS_TOKEN"], "serpapi_key": ["SERPAPI_KEY"], "hf_token": ["HF_TOKEN"], "fish_key": ["FISH_API_KEY"]}


# todas as chaves secretas: nome no Ajustes → variável no .env
SEGREDOS = {k: v[0] for k, v in ENV_CHAVES.items()}
SEGREDOS["anthropic_key"] = "ANTHROPIC_API_KEY"


def _ler_env():
    """Lê o .env (linhas CHAVE=valor; # comentário; aspas opcionais)."""
    d = {}
    try:
        for ln in ENV_ARQ.read_text(encoding="utf-8-sig").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            d[k.strip()] = v
    except Exception:
        pass
    return d


def _gravar_env(novos: dict):
    """Atualiza/cria só as variáveis pedidas no .env, mantendo o resto do arquivo."""
    linhas = []
    try:
        linhas = ENV_ARQ.read_text(encoding="utf-8-sig").splitlines()
    except Exception:
        pass
    pend = dict(novos)
    for i, ln in enumerate(linhas):
        k = ln.split("=", 1)[0].strip()
        if "=" in ln and not ln.lstrip().startswith("#") and k in pend:
            linhas[i] = f"{k}={pend.pop(k)}"
    for k, v in pend.items():
        linhas.append(f"{k}={v}")
    ENV_ARQ.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def env_chaves(base=None):
    """os.environ + as chaves salvas no painel (a do painel não sobrescreve uma que já exista no sistema)."""
    import os
    env = dict(base if base is not None else os.environ)
    a = ler()
    for k, nomes in ENV_CHAVES.items():
        v = str(a.get(k) or "").strip()
        for n in nomes:
            if v and not env.get(n):
                env[n] = v
    return env


def ler():
    d = dict(PADRAO)
    if ARQ.exists():
        try:
            d.update({k: v for k, v in json.loads(ARQ.read_text(encoding="utf-8-sig")).items() if k in PADRAO})
        except Exception:
            pass
    env = _ler_env()
    for k, var in SEGREDOS.items():          # a chave do .env manda; se não tiver, vale a que estiver no ajustes.json (compatível com o antigo)
        if env.get(var):
            d[k] = env[var]
    if d.get("idioma") not in IDIOMAS:
        d["idioma"] = "pt-BR"
    if d.get("voz") in ("edge:pt-BR-AntonioNeural", "edge:pt-BR-FranciscaNeural"):   # vozes robóticas: proibidas (07/11) → Thalita
        d["voz"] = "edge:pt-BR-ThalitaMultilingualNeural"
    return d


def salvar(novos: dict):
    d = ler()
    for k, v in (novos or {}).items():
        if k in PADRAO:
            d[k] = str(v or "").strip() if isinstance(PADRAO[k], str) else v
    for k in ("modelo_ollama", "voz", "pasta_saida", "fish_modelo"):
        if not d.get(k):
            d[k] = PADRAO[k]
    segredos = {SEGREDOS[k]: str(d.get(k) or "").strip() for k in SEGREDOS if k in (novos or {}) or (d.get(k) and not _ler_env().get(SEGREDOS[k]))}
    if segredos:
        _gravar_env(segredos)                # chaves vão pro .env (inclui mover as que ainda estavam no ajustes.json)
    ARQ.write_text(json.dumps({k: ("" if k in SEGREDOS else v) for k, v in d.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
    return d


def idioma_llm(cod=None):
    return IDIOMAS.get(cod or ler()["idioma"], IDIOMAS["pt-BR"])["llm"]
