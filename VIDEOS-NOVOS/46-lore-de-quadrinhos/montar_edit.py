import json, os
D = os.path.dirname(os.path.abspath(__file__))
DUR = 70.6
pages = [
 ("pg1","intro",0.0,7.9,{"cam":"0,2.1,5.0","c1":"Este herói você nunca viu","c2":"Inventado para este vídeo","c3":"Mas a época é real"}),
 ("pg2","ano",7.9,16.9,{"cam":"7.9,10.3,11.7,13.5","ano":"1941","c1":"Estados Unidos","c2":"Um gibi: 10 centavos de dólar","c3":"Bancas lotadas de mascarados"}),
 ("pg3","origem",16.9,28.4,{"cam":"16.9,19.4,22.7,26.4","titulo":"O FAROLEIRO","c0":"Personagem fictício","c1":"Eli Moura cuida de um farol numa ilha da costa","c2":"Uma noite de tempestade...","som":"KRA-KOOM!","c3":"...e a luz entra nele"}),
 ("pg4","poderes",28.4,34.5,{"cam":"28.4,30.7,33.0","c1":"Agora ele enxerga no escuro","c2":"Um feixe que guia navios...","c3":"...e cega bandido","som":"FZZAP!"}),
 ("pg5","lutas",34.5,47.5,{"cam":"34.5,38.3,40.4,43.7","zoom":[None,None,None,[60,540,1260,430]],"c1":"Contrabandistas no porto","som1":"POW!","c2":"Depois, sabotadores","som2":"TSSSS","capa":"FAROLEIRO","som3":"SOCK!","c3":"Na guerra, capas assim eram comuns"}),
 ("pg6","queda",47.5,58.6,{"cam":"47.5,49.4,51.7,55.1","em_capas":"51.74,52.48,52.94,53.52","em_carimbo":56.9,"ano":"1945","c1":"A guerra acaba","c2":"E o leitor muda","capa":"FAROLEIRO","carimbo":"CANCELADO"}),
 ("pg7","fim",58.6,66.0,{"cam":"58.6,60.6,63.4","em_apaga":60.7,"c1":"E o Faroleiro?","c2":"Apaga a luz pela última vez","fim":"FIM?","c3":"Mais um herói esquecido dos anos 40"}),
 ("pg8","cta",66.0,DUR,{"cam":"66.0","c1":"Quer ele de volta? Comenta:","palavra":"FAROL"}),
]
items = []
for pid, sc, s, e, p in pages:
    items.append({"id": pid, "type": "scene", "track": "fundo", "label": f"Página {sc}", "start": s, "dur": round(e - s, 2),
                  "by": "template", "props": {"scene": sc, "params": p}})
extra = []
for i, (_, _, s, _, _) in enumerate(pages[1:]):
    extra.append({"id": f"w{i+1}", "src": "audio/whoosh.wav", "start": round(max(0, s - 0.25), 2), "volume": 0.22, "label": "whoosh troca de página"})
edit = {
 "version": 1,
 "name": "46 - LORE DE QUADRINHOS - A origem de um herói esquecido dos anos 40",
 "estilo": "LORE DE QUADRINHOS — câmera passeando por páginas de HQ próprias (SVG)",
 "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#1a1712"},
 "duration": DUR,
 "template": "local",
 "fonts": {"Bangers": "fonts/Bangers-Regular.ttf", "ComicNeue": "fonts/ComicNeue-Bold.ttf"},
 "referencia": {
   "canal": "Comics Explained",
   "canal_url": "https://www.youtube.com/channel/UCKxQmKgrkUv4S7P5w0pLayw",
   "video": "https://www.youtube.com/watch?v=4NtPYpaXYXc",
   "titulo": "Marvel Comics: Kang The Conqueror Explained",
   "secundaria": {"canal": "MerryMarvelite", "canal_url": "https://www.youtube.com/channel/UC2P_2LRlG6IJM2QRvv7S5Gg",
                   "video": "https://www.youtube.com/watch?v=E9BRnMfiDf4", "titulo": "The Complete Canon Origin of Wolverine"},
   "nota": "só o estilo (câmera sobre painéis de HQ + narração); herói, desenhos e páginas 100% próprios em SVG"},
 "audio": {
   "voice": {"src": "audio/voz.mp3", "volume": 1.0, "start": 0},
   "music": {"src": "audio/musica.mp3", "volume": 0.10, "start": 0, "fade_out": 2.5, "duck": True},
   "extra": extra},
 "tracks": [{"id": "fundo", "name": "Páginas de HQ"}],
 "items": items,
}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(items))
