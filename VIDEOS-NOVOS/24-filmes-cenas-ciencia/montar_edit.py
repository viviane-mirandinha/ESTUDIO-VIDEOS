import os
﻿import json, os, re
O = os.path.dirname(os.path.abspath(__file__))
NAME = "24 - FILMES BASTIDORES - Quando o diretor contratou um sargento de verdade"
DUR = 64.66
CR = json.load(open(os.path.join(O, "img", "creditos.json"), encoding="utf-8"))
items = []

def credito(src):
    if src.startswith("f_"): return "Ilustração IA"
    if src.startswith("tr_"): return "Trailer oficial · Warner Bros."
    c = CR.get(src + ".jpg")
    if not c: return ""
    if c["license"].lower().startswith("public"):
        return "Trailer Dr. Strangelove · domínio público" if src == "kub_trailer" else "Domínio público"
    art = re.split(r" from | \(|,", c["artist"])[0].strip()[:34]
    return f"{art} · {c['license']}"

def foto(id, s, e, src, motion="zoom_in", amount=0.07, nome="", sub="", centro="", bw=0, moldura=0, pos="50% 50%", fo=0, label=""):
    if src.startswith("tr_"): moldura = 1
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label or f"Still {src}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "dc_still", "params": {"src": "img/" + src + ".jpg", "motion": motion, "amount": amount, "pos": pos,
                            "bw": bw, "moldura": moldura, "centro": centro, "nome": nome, "sub": sub, "credito": credito(src),
                            "fade_in": 0.3 if s > 0 else 0, "fade_out": fo}}})

def cap(id, s, e, n, titulo, topo=0):
    items.append({"id": id, "type": "scene", "track": "textos", "label": f"Capítulo {n}: {titulo}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "dc_capitulo", "params": {"n": n, "titulo": titulo, "topo": topo}}})

foto("s01", 0.0, 3.10, "kub_1949", "zoom_in", 0.08, "Stanley Kubrick", "o diretor", bw=1, label="Kubrick 1949")
foto("s02", 3.10, 5.10, "vn_patrol", "zoom_in", 0.10, bw=1, label="Vietnã 1968 (guerra de verdade)")
foto("s03", 5.10, 7.20, "f_bastidores", "zoom_in", 0.06, centro="1985", label="Set escuro + 1985")
foto("s04", 7.20, 10.30, "erm_618", "zoom_in", 0.08, "R. Lee Ermey", "ex-fuzileiro naval", label="Ermey retrato")
foto("s05", 10.30, 12.40, "vn_mount", "pan_left", 0.10, centro="14 meses de Vietnã", bw=1, label="Vietnã 14 meses")
foto("s06", 12.40, 15.10, "fmj_helm", "zoom_in", 0.08, centro="Consultor técnico", moldura=1, label="Capacete do filme (expo)")
foto("s07", 15.10, 16.66, "tr_12", "zoom_in", 0.04, "Nascido para Matar", label="Trailer: marcha")
foto("s08", 16.66, 19.86, "f_set", "zoom_in", 0.08, "Os ensaios", label="Set ensaio (IA)")
foto("s09", 19.86, 21.60, "tr_20", "zoom_in", 0.04, "Os recrutas", label="Trailer: recrutas")
foto("s10", 21.60, 23.06, "f_recrutas", "zoom_in", 0.07, centro="com educação", label="Recrutas (IA)")
foto("s11", 23.06, 24.20, "erm_085", "zoom_in", 0.10, "Ermey explodiu", label="Ermey falando às tropas")
foto("s12", 24.20, 26.16, "tr_90", "zoom_in", 0.05, "“Ninguém fala assim com um recruta!”", label="Trailer: Hartman grita")
foto("s13", 26.16, 28.20, "kub_a", "zoom_in", 0.07, bw=1, pos="50% 40%", label="Kubrick calado")
foto("s14", 28.20, 31.90, "erm_uni", "zoom_in", 0.06, "R. Lee Ermey", "o sargento", moldura=1, pos="50% 30%", label="Ermey uniforme")
foto("s15", 31.90, 34.94, "fmj_heli", "pan_left", 0.08, "O atirador do helicóptero", label="Helicóptero do filme (expo)")
foto("s16", 34.94, 36.58, "f_roteiro", "zoom_in", 0.07, centro="Não decorou falas", label="Roteiro (IA)")
foto("s17", 36.58, 38.40, "tr_30", "zoom_in", 0.04, "Ordens reais", label="Trailer: ordens")
foto("s18", 38.40, 40.20, "tr_46", "zoom_in", 0.04, "Extras de verdade", label="Trailer: extras")
foto("s19", 40.20, 42.20, "tr_88", "zoom_in", 0.04, "Insultos improvisados", label="Trailer: insultos")
foto("s20", 42.20, 44.60, "kub_spart", "zoom_in", 0.07, bw=1, label="Kubrick no set")
foto("s21", 44.60, 46.76, "f_claquete", "zoom_in", 0.07, label="Claquete (IA)")
foto("s22", 46.76, 49.20, "kub_trailer", "zoom_in", 0.08, "O próprio diretor", bw=1, label="Kubrick close")
foto("s23", 49.20, 52.30, "erm_618", "zoom_out", 0.10, centro="Ódio ou atuação?", pos="50% 35%", label="Ermey ódio?")
foto("s24", 52.30, 55.10, "f_elenco", "zoom_in", 0.07, "O elenco", "nos bastidores", label="Elenco bastidores (IA)")
foto("s25", 55.10, 58.20, "fmj_tiff", "zoom_in", 0.07, centro="Inscreva-se", sub="para mais bastidores que Hollywood esconde", moldura=1, label="Expo FMJ + inscreva-se")
foto("s26", 58.20, 61.00, "erm_dm", "zoom_in", 0.07, "R. Lee Ermey", label="Ermey com fuzileiros")
foto("s27", 61.00, DUR, "f_bastidores", "zoom_out", 0.06, centro="O sargento que dirigiu a si mesmo", fo=1.2, label="Fecho")
cap("c1", 5.20, 7.15, "1", "O consultor", topo=1)
cap("c2", 28.25, 29.90, "2", "O papel")
cap("c3", 49.25, 50.90, "3", "Os bastidores", topo=1)
items.append({"id": "t1", "type": "scene", "track": "textos", "label": "Takes: dezenas -> poucas", "start": 43.30, "dur": 3.40,
              "props": {"scene": "dc_troca", "params": {"de": "dezenas de takes", "para": "poucas tomadas", "t_risca": 1.3, "t_para": 2.0}}})

fundo = sorted([i for i in items if i["track"] == "fundo"], key=lambda i: i["start"])
for a, b in zip(fundo, fundo[1:]):
    a["dur"] = round(max(a["dur"], b["start"] + 0.35 - a["start"]), 2)

edit = {
    "version": 1, "name": NAME, "estilo": "24-filmes-cenas-ciencia", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"}, "duration": DUR, "template": "generic",
    "fonts": {"Barlow": "fonts/BarlowCondensed-Bold.ttf", "Outfit": "fonts/Outfit.ttf"},
    "referencia": {"canal": "Director's Cut.", "canal_url": "https://www.youtube.com/channel/UC0UMbbooWjYX6twoYAIC5OA",
                   "video": "https://youtu.be/gLtO6ZfKt3c", "titulo": "When the Director Hires a REAL Drill Instructor",
                   "nota": "Stills em tela cheia com Ken Burns, card 'Capítulo N:' em sans condensada branca, rótulo de personagem centrado embaixo, fotos P&B de bastidor; frames do trailer só como still ≤2 s emoldurado."},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.12, "start": 0, "fade_out": 2.0, "duck": True}, "extra": []},
    "tracks": [{"id": "fundo", "name": "Stills"}, {"id": "textos", "name": "Textos"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items), "trailer_frames", sum(1 for i in items if "tr_" in str(i["props"]["params"].get("src", ""))))
