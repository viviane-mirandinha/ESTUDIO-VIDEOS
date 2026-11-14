# Monta edit.json do vídeo 21 (this or that) a partir dos tempos do words.json
import json, os
O = os.path.dirname(os.path.abspath(__file__)); os.chdir(O)
NAME = "21 - CARDS PRODUTO THIS OR THAT - Isso ou aquilo monte seu setup de estudos"
DUR = 85.0
# (pergunta, rótulo A, rótulo B, escolha, detalhe, t_pergunta, t_resposta)  — tempos do words.json
P = [
 ("Mesa ou escrivaninha?", "Mesa", "Escrivaninha", "a", "", 0.0, 1.44),
 ("Cadeira gamer ou ergonômica?", "Gamer", "Ergonômica", "b", "", 2.24, 4.5),
 ("Monitor único ou duplo?", "Único", "Duplo", "b", "", 5.48, 7.32),
 ("Notebook aberto ou fechado?", "Aberto", "Fechado", "b", "modo clamshell", 8.16, 10.28),
 ("Teclado mecânico ou membrana?", "Mecânico", "Membrana", "a", "switch silencioso", 12.16, 14.18),
 ("Mouse vertical ou tradicional?", "Vertical", "Tradicional", "a", "alivia o pulso", 16.52, 18.62),
 ("Lâmpada fria ou quente?", "Fria", "Quente", "b", "3000K, menos cansaço", 20.62, 22.4),
 ("Fone over-ear ou intra-auricular?", "Over-ear", "Intra-auricular", "a", "isolamento passivo", 24.88, 27.08),
 ("Papel ou tablet para anotações?", "Papel", "Tablet", "a", "fixa melhor a memória", 29.14, 31.46),
 ("Parede lisa ou quadro de cortiça?", "Parede lisa", "Cortiça", "b", "organiza prazos visuais", 33.64, 36.22),
 ("Café ou água?", "Café", "Água", "b", "água primeiro, café depois", 38.86, 39.96),
 ("Silêncio total ou ruído branco?", "Silêncio total", "Ruído branco", "b", "mascara conversas", 42.02, 44.22),
 ("Pomodoro ou bloco longo?", "Pomodoro", "Bloco longo", "a", "25 e 5", 46.72, 48.62),
 ("Celular na mesa ou na gaveta?", "Na mesa", "Na gaveta", "b", "fora do campo visual", 50.66, 52.98),
 ("Planner físico ou app?", "Planner físico", "App", "b", "sincroniza com a nuvem", 55.0, 56.94),
 ("Tapete de mouse grande ou pequeno?", "Grande", "Pequeno", "a", "cobre a área toda", 59.0, 61.32),
 ("Suporte de notebook ou livros?", "Suporte", "Livros", "a", "altura dos olhos", 63.38, 65.76),
 ("Cabo solto ou organizador?", "Cabo solto", "Organizador", "b", "evita enrosco", 67.66, 70.1),
 ("Planta artificial ou natural?", "Artificial", "Natural", "b", "melhora o ar", 71.92, 73.84),
]
T_RECAP, T_CTA1, T_CTA2 = 75.3, 77.75, 81.5
items = [{"id": "fundo", "type": "image", "track": "fundo", "label": "Fundo papel", "start": 0, "dur": DUR,
          "props": {"src": "img/fundo.svg", "fill": True, "fit": "cover", "motion": "none"}}]
recap = {}
for i, (q, ra, rb, e, det, tq, tr) in enumerate(P):
    n = i + 1; t0 = max(0.0, tq - 0.08)
    t1 = (P[i + 1][5] - 0.08) if i + 1 < len(P) else T_RECAP
    items.append({"id": f"par{n:02d}", "type": "scene", "track": "visual", "label": f"{n:02d} {q}", "start": round(t0, 2), "dur": round(t1 - t0, 2),
                  "props": {"scene": "tot_par", "params": {"titulo": q, "n": f"{n}/19", "isso": "Isso", "aquilo": "Aquilo",
                            "a_img": f"img/p{n:02d}a.jpg", "a_rot": ra, "b_img": f"img/p{n:02d}b.jpg", "b_rot": rb,
                            "escolha": e, "t_resp": round(tr - t0, 2), "detalhe": det, "cor": "#c8102e"}}})
    recap[f"i{n:02d}"] = f"img/p{n:02d}{e}.jpg"
items.append({"id": "recap", "type": "scene", "track": "visual", "label": "Recap: setup montado", "start": T_RECAP, "dur": round(DUR - T_RECAP, 2),
              "props": {"scene": "tot_recap", "params": dict({"titulo": "Seu setup ideal", "sub": "montado", "cor": "#c8102e", "stagger": 0.07}, **recap)}})
items.append({"id": "cta1", "type": "text", "track": "textos", "label": "CTA comentário", "start": T_CTA1, "dur": round(T_CTA2 - T_CTA1, 2), "in": "slide_up", "out": "fade",
              "props": {"text": "Mais de 10 iguais? Comenta qual faltou", "x": 640, "y": 625, "w": 1100, "size": 48, "color": "#1d1d1f", "font": "Montserrat",
                        "weight": 800, "align": "center", "bg": "rgba(255,255,255,.92)", "pad": 16, "radius": 18, "shadow": True,
                        "highlight": ["Comenta qual faltou"], "hl_color": "#c8102e"}})
items.append({"id": "cta2", "type": "text", "track": "textos", "label": "CTA inscreva-se", "start": T_CTA2, "dur": round(DUR - T_CTA2, 2), "in": "slide_up", "out": "none",
              "props": {"text": "Inscreva-se para mais comparações", "x": 640, "y": 625, "w": 1100, "size": 50, "color": "#ffffff", "font": "Montserrat",
                        "weight": 800, "align": "center", "bg": "#c8102e", "pad": 18, "radius": 18, "shadow": True}})
ed = {"version": 1, "name": NAME, "estilo": "21-cards-produto-this-or-that", "grupo": "ESTILOS NOVOS",
      "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#f4f0ea"}, "duration": DUR, "template": "generic",
      "fonts": {"Montserrat": "fonts/Montserrat-Bold.ttf", "GeorgiaBI": "fonts/georgiaz.ttf"},
      "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}},
      "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "visual", "name": "Cards this or that"}, {"id": "textos", "name": "Textos / CTA"}],
      "referencia": {"canal": "YourVibeChoice", "canal_url": "https://www.youtube.com/@YourVibeChoice", "video": "https://youtu.be/ubRkkpLfIHU",
                     "titulo": "This or That: Build Your Dream Fall Shopping!", "nota": "cards this-or-that em fundo papel com rabiscos vermelhos; 2a ref: @deskstandard (narração calma)"},
      "items": items}
json.dump(ed, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("edit.json ok", len(items), "itens")
