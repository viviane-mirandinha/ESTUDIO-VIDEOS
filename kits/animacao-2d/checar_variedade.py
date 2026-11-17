# checar_variedade.py — GUARDA contra cena repetida (zero token).
# Uso: python kits/animacao-2d/checar_variedade.py <pasta-do-video>      (lê edit.json + catalogo.json)
import sys, json, pathlib
K = pathlib.Path(__file__).parent; pasta = pathlib.Path(sys.argv[1])
cat = {k: v for k, v in json.loads((K / "catalogo.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
ed = json.loads((pasta / "edit.json").read_text(encoding="utf-8"))
cenas = sorted([i for i in ed["items"] if i.get("type") == "scene" and i.get("by") == "template"], key=lambda i: i["start"])
erros = []
JAN_TIPO, JAN_FICHA = 3, 12     # mesma cena só volta depois de 8; mesmo (local+vista+ação) só depois de 12
fichas = []
for n, c in enumerate(cenas):
    tipo = c["props"]["scene"]; f = cat.get(tipo)
    if not f: erros.append(f"{c['id']}: tipo de cena \"{tipo}\" não tem ficha em catalogo.json"); fichas.append(None); continue
    fichas.append(f)
    if not str(c.get("fala", "")).strip(): erros.append(f"{c['id']} ({tipo}): falta o campo \"fala\" (o trecho da narração que esta cena ilustra)")
    if f["acao"] == "andar" and not str(c.get("porque", "")).strip(): erros.append(f"{c['id']} ({tipo}): personagem anda mas falta \"porque\" (para onde vai e por que a fala justifica)")
    lim = 9.0 if str(c.get("longa", "")).strip() else 6.0
    if c["dur"] > lim: erros.append(f"{c['id']} ({tipo}): cena de {c['dur']:.1f} s — passa de {lim:.0f} s" + ("" if lim == 9.0 else " (parece parado; se for plano calmo/revelação em sequência, explique no campo \"longa\")"))
    if c.get("continua"): continue      # mesmo plano em etapas (ex.: trio que vai ganhando personagens) — intencional
    for m in range(max(0, n - JAN_TIPO), n):
        if cenas[m]["props"]["scene"] == tipo: erros.append(f"{c['id']} repete o tipo \"{tipo}\" de {cenas[m]['id']} (mínimo {JAN_TIPO} cenas de distância)")
    for m in range(max(0, n - JAN_FICHA), n):
        g = fichas[m]
        if g and (g["local"], g["vista"], g["acao"]) == (f["local"], f["vista"], f["acao"]) and cenas[m]["props"]["scene"] != tipo:
            erros.append(f"{c['id']} é o mesmo plano de {cenas[m]['id']} (local \"{f['local']}\" + vista \"{f['vista']}\" + ação \"{f['acao']}\") — mude o local, a vista ou a ação")
    if n and fichas[n - 1]:
        g = fichas[n - 1]
        if g["local"] == f["local"]:
            iguais = sum(g[k] == f[k] for k in ("vista", "acao", "camera"))
            if iguais > 1: erros.append(f"{c['id']} e {cenas[n-1]['id']} seguidas no mesmo local \"{f['local']}\" e quase iguais (mude pelo menos 2 de: vista, ação, câmera)")
    if n >= 4 and all(fichas[n - k] and fichas[n - k]["vista"] == f["vista"] for k in range(0, 5)):
        erros.append(f"{c['id']}: 5 cenas seguidas com a mesma vista \"{f['vista']}\" — alterne frente/perfil/costas/close")
for n in range(len(cenas) - 4):
    jan = fichas[n:n + 5]
    if all(jan) and sum(1 for g in jan if g["acao"] == "andar") > 2:
        erros.append(f"de {cenas[n]['id']} a {cenas[n+4]['id']}: mais de 2 cenas de caminhada em 5 — o personagem vive andando; alterne com cenas paradas/objetos")
for n in range(len(cenas)):                       # RITMO DE CORTES: o original tem 1 corte a cada ~5,6 s (mediana 3,9 s)
    ini = cenas[n]["start"]; cortes = [x["start"] for x in cenas if ini < x["start"] <= ini + 8.0]
    if len(cortes) > 2: erros.append(f"{len(cortes)} cortes em 8 s a partir de {ini:.1f} s ({cenas[n]['id']}) — máximo 2 (o original tem ~1 corte a cada 4–6 s); junte cenas ou alongue")
    if cenas[n]["dur"] < 2.0 and n not in (0, len(cenas) - 1): erros.append(f"{cenas[n]['id']}: cena de {cenas[n]['dur']:.1f} s — curta demais (mínimo 2,0 s)")
if cenas:
    media = sum(c["dur"] for c in cenas) / len(cenas)
    if media > 7.0: erros.append(f"duração média das cenas {media:.1f} s — passa de 7 s (o original: ~5,6 s)")
    if media < 3.0: erros.append(f"duração média das cenas {media:.1f} s — abaixo de 3 s (cortes demais; o original: ~5,6 s)")
print(f"{len(cenas)} cenas, {len({c['props']['scene'] for c in cenas})} tipos diferentes")
if erros: print("REPROVADO (variedade):"); [print("  ✗ " + e) for e in erros]; sys.exit(1)
print("APROVADO (variedade)")
