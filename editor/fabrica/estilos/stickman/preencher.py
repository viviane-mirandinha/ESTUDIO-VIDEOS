# preencher.py — estilo "stickman" (Stickman Studio). Escrito do zero para o Estúdio de Vídeos.
# Entrada: ctx (video_imagens.montar) = {nome, titulo, canal, duracao, words, shots:[{s,e,texto,words}], voz, cta_tempos, roteiro,
#          pasta, idioma, ollama, modelo, vertical}
# Saída: edit.json (template generic). Cada frase = 1 item "scene" (templates/scenes/stickman.html) com params editáveis:
#   pose · fala (balão) · destaque (texto-chave grande) · cenario · lado · pose2/fala2 (2º boneco) · cor · desenhar · entrada
# A IA local (Ollama) escolhe pose/cenário/texto de cada frase; se ela falhar, regras simples por palavra-chave.
import json
import re

POSES = ["parado", "explicando", "apontando", "pensando", "surpreso", "comemorando", "andando", "triste"]
CENARIOS = ["chao", "casa", "cidade", "escritorio", "natureza", "quadro", "palco", "vazio"]
CORES = ["#ff5a36", "#2f7cf6", "#12a150", "#c026d3", "#f59e0b"]
TXT = {"pt-BR": {"insc": "Se inscreve aí!", "fim": "Valeu por assistir!"}, "en-US": {"insc": "Subscribe!", "fim": "Thanks for watching!"},
       "es-MX": {"insc": "¡Suscríbete!", "fim": "¡Gracias por ver!"}}


def _regras(texto, i):
    t = texto.lower()
    if "?" in texto or re.search(r"\b(por que|porque|será|como assim|imagina|pensa)\b", t):
        pose = "pensando"
    elif re.search(r"\b(incr[ií]vel|uau|nossa|choc|surpre|ningu[eé]m|nunca|segredo|\d{3,})", t) or "!" in texto:
        pose = "surpreso"
    elif re.search(r"\b(consegu|venc|sucesso|ganh|feliz|parab|melhor|vit[oó]ria)", t):
        pose = "comemorando"
    elif re.search(r"\b(and|caminh|viaj|corr|ir |vai |foi |cheg|sa[ií])", t):
        pose = "andando"
    elif re.search(r"\b(triste|perd|problema|dif[ií]cil|ruim|medo|morr)", t):
        pose = "triste"
    else:
        pose = ["explicando", "apontando", "parado", "explicando"][i % 4]
    cen = "chao"
    for rx, c in ((r"casa|fam[ií]lia|quarto|cozinha", "casa"), (r"cidade|rua|pr[eé]dio|carro|tr[aâ]nsito", "cidade"),
                  (r"trabalh|empresa|escrit[oó]rio|chefe|computador|dinheiro|sal[aá]rio", "escritorio"),
                  (r"natureza|[aá]rvore|floresta|animal|planta|sol|mar|rio|c[eé]u", "natureza"),
                  (r"aprend|estud|escola|ci[eê]ncia|regra|passo|dica|ensin", "quadro")):
        if re.search(rx, t):
            cen = c
            break
    nums = re.findall(r"\d[\d.,]*\s*(?:%|mil|milh[õo]es|bilh[õo]es|anos|dias|horas|metros|km|kg)?", texto)
    if nums:
        dest = nums[0].strip()
    else:
        ws = [w.strip(".,!?;:\"'()") for w in texto.split()]
        ws = [w for w in ws if len(w) > 4]
        dest = max(ws, key=len).upper() if ws else ""
    return {"pose": pose, "cenario": cen, "destaque": dest[:28], "fala": ""}


def _norm(s):
    import unicodedata
    return re.sub(r"[^a-z0-9 ]+", "", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())


def _na_frase(dest, frase):
    f = _norm(frase).split()
    return all(w in f for w in _norm(dest).split())


def _ia(ctx, shots):
    """1 chamada por lote de 8 frases → [{pose, cenario, destaque, fala}]"""
    oll, modelo = ctx.get("ollama"), ctx.get("modelo")
    if not oll:
        return {}
    out = {}
    for ini in range(0, len(shots), 8):
        lote = shots[ini:ini + 8]
        lista = "\n".join(f"{ini + k}: {s['texto']}" for k, s in enumerate(lote))
        prompt = (f"Você dirige um vídeo de bonecos de palito (stickman). Para CADA frase numerada da narração, escolha:\n"
                  f"- pose do boneco: uma de {POSES}\n- cenario: um de {CENARIOS} (repita o mesmo cenário em frases seguidas do mesmo assunto)\n"
                  f"- destaque: o texto-chave grande na tela, 1 a 4 palavras TIRADAS da frase (número, nome ou ideia principal)\n"
                  f"- fala: o que o boneco diz no balão, no máximo 5 palavras, reação curta e natural (ou \"\" em metade das frases)\n"
                  f"- dois: true só se a frase fala de duas pessoas/conversa\n"
                  f"Idioma dos textos: o mesmo da narração. Responda SÓ JSON: {{\"cenas\": [{{\"i\": 0, \"pose\": \"...\", \"cenario\": \"...\", \"destaque\": \"...\", \"fala\": \"...\", \"dois\": false}}]}}\n\n"
                  f"Frases:\n{lista}")
        try:
            d = oll._json_seguro(oll.gerar(prompt, modelo, json_mode=True, temperatura=0.4, num_predict=900, timeout=180))
            for c in (d.get("cenas") or []):
                try:
                    out[int(c.get("i"))] = c
                except Exception:
                    pass
        except Exception as e:
            print(f"stickman: IA falhou no lote {ini} ({str(e)[:80]}) — usando regras", flush=True)
    return out


def preencher(ctx):
    vert = bool(ctx.get("vertical"))
    W, H = (1080, 1920) if vert else (1280, 720)
    DUR = float(ctx["duracao"])
    shots = ctx["shots"]
    tx = TXT.get(ctx.get("idioma") or "pt-BR", TXT["pt-BR"])
    ia = _ia(ctx, shots)
    cor = CORES[sum(map(ord, ctx.get("titulo") or "x")) % len(CORES)]
    items, ant_cen, ant_lado = [], None, None
    fim_cards = 2.6
    shots = [sh for k, sh in enumerate(shots) if k == 0 or sh["s"] < DUR - fim_cards - 0.8]   # nada por cima do cartão final
    for i, sh in enumerate(shots):
        r = _regras(sh["texto"], i)
        c = ia.get(i) or {}
        pose = c.get("pose") if c.get("pose") in POSES else r["pose"]
        cen = c.get("cenario") if c.get("cenario") in CENARIOS else r["cenario"]
        dest = str(c.get("destaque") or "").strip()[:32]
        if dest and not _na_frase(dest, sh["texto"]):   # a IA às vezes inventa/erra a grafia → só vale o que foi falado
            dest = ""
        dest = dest or r["destaque"]
        if len(dest.split()) > 5:
            dest = " ".join(dest.split()[:4])
        fala = str(c.get("fala") or "").strip()[:40]
        if len(fala.split()) > 6:
            fala = ""
        dois = bool(c.get("dois")) and not vert
        lado = "esq" if (i // 3) % 2 == 0 else "dir"   # troca de lado a cada ~3 frases (dá movimento)
        if i == 0:
            tt = (ctx.get("titulo") or dest).strip()
            dest = tt if len(tt) <= 60 else tt[:60].rsplit(" ", 1)[0] + "…"
            pose, fala = ("apontando" if pose in ("parado", "triste") else pose), ""
        st = round(sh["s"] if i else 0.0, 2)
        fim = round(shots[i + 1]["s"], 2) if i + 1 < len(shots) else round(DUR - fim_cards, 2)
        params = {"pose": pose, "fala": fala, "destaque": dest, "cenario": cen, "lado": lado, "cor": cor,
                  "desenhar": cen != ant_cen, "entrada": "anda" if (i == 0 or lado != ant_lado) else "nada"}
        if dois:
            params.update({"pose2": "explicando" if pose != "explicando" else "pensando", "fala2": ""})
        items.append({"id": f"c{i:02d}", "type": "scene", "track": "fundo", "label": f"Cena {i + 1}: {sh['texto'][:40]}", "start": st,
                      "dur": round(max(0.6, fim - st), 2), "in": "none", "out": "none", "props": {"scene": "stickman", "params": params}})
        ant_cen, ant_lado = cen, lado
    # cartão final: boneco comemorando + canal
    t0 = round(DUR - fim_cards, 2)
    items.append({"id": "fim", "type": "scene", "track": "fundo", "label": "Cartão final", "start": t0, "dur": fim_cards, "in": "none", "out": "none",
                  "props": {"scene": "stickman", "params": {"pose": "comemorando", "fala": tx["insc"], "destaque": ctx.get("canal") or "", "cenario": "palco",
                                                            "lado": "esq", "cor": cor, "desenhar": True, "entrada": "pula"}}})
    cap = {"words_file": "words.json", "per_group": 2 if vert else 3, "x": W // 2, "y": int(H * (0.785 if vert else 0.935)), "size": 76 if vert else 50,
           "color": "#1c1c1c", "dim": "rgba(28,28,28,.45)", "hl_color": cor, "font": "Patrick Hand", "weight": 800,
           "bg": "rgba(255,255,255,.88)", "upper": False}
    items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": round(DUR - fim_cards, 2), "in": "none", "out": "none",
                  "props": cap})
    return {"version": 1, "name": ctx["nome"], "estilo": "Stickman Studio", "canvas": {"w": W, "h": H, "fps": 30, "bg": "#f7f4ec"},
            "duration": DUR, "template": "generic",
            "head": '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap">',
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0},
                      **({"music": {"src": ctx["musica"], "volume": 0.1, "start": 0, "fade_out": 2.0, "duck": True}} if ctx.get("musica") else {})},
            "tracks": [{"id": "fundo", "name": "Cenas (bonecos)"}, {"id": "legenda", "name": "Legenda"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/estilos/stickman/preencher.py", "cena": "templates/scenes/stickman.html"}}
