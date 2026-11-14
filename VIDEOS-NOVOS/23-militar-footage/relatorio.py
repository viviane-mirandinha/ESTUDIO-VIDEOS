import json,sys,datetime
ini="2026-10-22T14:57:26-03:00"; fim=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
m=round((datetime.datetime.fromisoformat(fim)-datetime.datetime.fromisoformat(ini)).total_seconds()/60,1)
R={"video":23,"estilo":"23-militar-footage","inicio":ini,"fim":fim,"minutos":m,"render_segundos":int(sys.argv[1]),
"observacoes":sys.argv[2],
"estimativa_30min":{"horas_maquina":2.5,"o_que_escala":"Cenas novas reaproveitáveis (hud-drone, termico, mapa-tatico, mil-relatorio): vídeo novo = edit.json com cortes + params do mapa (câmera, marcas, rótulos, tiros). 30 min ≈ 450 cortes: busca/curadoria de stock militar livre (~1 h, Pixabay tem pouco militar; DVIDS sem API key), Flux local ~10 s/imagem, render draft ~20-30 min."}}
open("RELATORIO.json","w",encoding="utf-8").write(json.dumps(R,ensure_ascii=False,indent=1))
print(m)
