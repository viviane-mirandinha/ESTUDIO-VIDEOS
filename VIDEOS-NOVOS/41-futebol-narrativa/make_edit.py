import json
NAME = "41 - 24-10-2026 - FUTEBOL NARRATIVA - A historia de Garrincha em 1 minuto"
DUR = 70.5
# (id, cena, inicio, fim, rotulo, params)  -- tempos tirados de words.json (faster-whisper)
S = [
 ("s01", "abertura", 0.0, 8.6, "Abertura - retrato + curva", {"foto": "img/retrato_duo.jpg", "rot1": "coluna torta", "rot2": "pernas tortas",
   "titulo1": "A HISTÓRIA DE", "titulo2": "GARRINCHA", "t_rot1": 1.0, "t_rot2": 1.84, "t_curva": 3.4, "t_titulo": 6.48, "t_nome": 7.32}),
 ("s02", "capitulo", 8.6, 10.8, "Capítulo 1", {"num": "CAPÍTULO 1", "titulo": "O PASSARINHO", "c1": "#1d2541", "c2": "#b8463a"}),
 ("s03", "nasce", 10.8, 17.0, "1933 - Pau Grande", {"nome": "MANUEL FRANCISCO DOS SANTOS", "ano": "1933", "local": "PAU GRANDE · RJ",
   "t_nome": 0.1, "t_ano": 2.36, "t_local": 3.9}),
 ("s04", "pernas", 17.0, 22.4, "Pernas - diagrama", {"rot_a": "para dentro", "rot_b": "para fora", "medida": "6 CM", "rot_medida": "mais curta",
   "t_a": 1.2, "t_b": 2.4, "t_medida": 3.4}),
 ("s05", "passaro", 22.4, 26.1, "Apelido - passarinho", {"foto": "img/corruira.jpg", "nome": "GARRINCHA", "sub": "= nome de um passarinho", "t_nome": 1.2, "t_sub": 1.7}),
 ("s06", "capitulo", 26.1, 28.4, "Capítulo 2", {"num": "CAPÍTULO 2", "titulo": "O DRIBLE", "c1": "#2f6b45", "c2": "#1d2541"}),
 ("s07", "clube", 28.4, 31.8, "1953 - Botafogo", {"ano": "1953", "clube": "BOTAFOGO", "t_ano": 0.28, "t_clube": 2.2}),
 ("s08", "campo", 31.8, 37.6, "Campo tático - o drible", {"rot_finta": "finta", "rot_arranque": "arrancada", "rot_jog": "G", "t_finta": 0.4, "t_arranque": 1.6, "t_carimbo": 3.9,
   "carimbo": "NINGUÉM PARAVA"}),
 ("s09", "capitulo", 37.6, 40.3, "Capítulo 3", {"num": "CAPÍTULO 3", "titulo": "AS COPAS", "c1": "#c99a1e", "c2": "#2f6b45"}),
 ("s10", "copas", 40.3, 45.0, "1958 e 1962 - cards", {"a1": "1958", "s1": "SUÉCIA", "a2": "1962", "s2": "CHILE", "rot": "CAMPEÃO DO MUNDO", "t1": 0.3, "t2": 2.5}),
 ("s11", "melhor", 45.0, 50.2, "1962 - melhor da Copa", {"foto": "img/fas_crop.jpg", "leg": "Garrincha com fãs, anos 60", "ano": "1962", "card": "PELÉ MACHUCADO",
   "fita": "ELEITO O MELHOR DA COPA", "t_card": 1.4, "t_fita": 3.9}),
 ("s12", "juntos", 50.2, 54.4, "Garrincha + Pelé = 0 derrotas", {"a": "GARRINCHA", "b": "PELÉ", "num": "0", "rot": "DERROTAS", "t_ab": 0.3, "t_num": 2.5}),
 ("s13", "capitulo", 54.4, 56.7, "Capítulo 4", {"num": "CAPÍTULO 4", "titulo": "A QUEDA", "c1": "#3a1f24", "c2": "#b8463a"}),
 ("s14", "queda", 56.7, 64.1, "Curva da carreira - queda", {"eixo_y": "talento", "eixo_x": "tempo", "pico": "auge · 1962", "rot1": "lesões no joelho", "rot2": "alcoolismo",
   "fim": "1983", "card": "49 ANOS", "t_rot1": 0.5, "t_rot2": 1.7, "t_fim": 4.16, "t_card": 5.8}),
 ("s15", "estadio", 64.1, 66.7, "Estádio Mané Garrincha", {"foto": "img/estadio_brasilia.jpg", "leg": "Estádio Nacional Mané Garrincha · Brasília"}),
 ("s16", "epitafio", 66.7, DUR, "Epitáfio - Alegria do Povo", {"local": "Magé, RJ", "l1": "AQUI DESCANSA A", "l2": "ALEGRIA DO POVO", "t_l2": 0.9}),
]
items = [{"id": i, "type": "scene", "track": "fundo", "label": lab, "start": a, "dur": round(b - a, 2), "by": "template",
          "props": {"scene": sc, "params": p}} for i, sc, a, b, lab, p in S]
items.append({"id": "regua", "type": "scene", "track": "visual", "label": "Linha do tempo da carreira", "start": 10.8, "dur": 53.3, "by": "template",
              "props": {"scene": "regua", "params": {"anos": ["1933", "1953", "1958", "1962", "1983"], "tempos": [13.16, 28.68, 41.32, 42.8, 60.86]}}})
LT = [("lt1", 3.4, 6.3, "UM DOS MAIORES DRIBLADORES DA HISTÓRIA"), ("lt2", 22.6, 3.4, "APELIDO DADO PELA IRMÃ"),
      ("lt3", 31.9, 3.7, "O DRIBLE ERA QUASE SEMPRE O MESMO"), ("lt5", 50.3, 2.1, "JUNTOS EM CAMPO")]
for i, a, d, t in LT:
    items.append({"id": i, "type": "text", "track": "textos", "label": "Faixa: " + t[:24], "start": a, "dur": round(d if d < 6 else d - a, 2), "by": "template",
                  "props": {"text": t}})
wh = [8.55, 26.05, 37.55, 54.35, 66.65]
E = {"version": 1, "name": NAME, "estilo": "41-futebol-narrativa", "grupo": "ESTILOS NOVOS",
     "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#e8eae3"}, "duration": DUR, "template": "local",
     "fonts": {"Bebas Neue": "fonts/BebasNeue-Regular.ttf", "Oswald": "fonts/Oswald-Bold.ttf", "Caveat": "fonts/Caveat.ttf"},
     "referencia": {"canal": "Tifo Football by The Athletic", "canal_url": "https://www.youtube.com/@Tifo",
                    "video": "https://www.youtube.com/watch?v=B7zPPImyTxI", "titulo": "The Rise & Fall of Ronaldinho",
                    "secundaria": {"canal": "Number 9", "video": "https://www.youtube.com/watch?v=ifodIYxyUtg",
                                   "titulo": "The Magician Who Brought Street Football to the World's Biggest Stadiums"},
                    "nota": "documentário de jogador ilustrado: papel quadriculado, recorte de foto com moldura branca e pontilhado, cartelas de capítulo em listras diagonais, faixas de legenda azul-marinho com amarelo condensado, gráfico de trajetória da carreira, campo tático desenhado"},
     "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
               "music": {"src": "musica.wav", "volume": 0.09, "start": 0, "fade_out": 2.5, "duck": True},
               "extra": [{"id": f"w{k}", "src": "sfx/whoosh.wav", "start": t, "volume": 0.16, "label": "whoosh"} for k, t in enumerate(wh)]},
     "tracks": [{"id": "fundo", "name": "Cenas"}, {"id": "visual", "name": "Linha do tempo"}, {"id": "textos", "name": "Faixas de legenda"}],
     "items": items}
json.dump(E, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items))
