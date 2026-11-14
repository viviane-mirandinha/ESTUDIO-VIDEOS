# Converte index.src.html -> template.html (formato do EDITOR VIDEOS, template local) + edit.json
import re, json
src = open('index.src.html', encoding='utf-8').read()
e0 = json.load(open('edit.json', encoding='utf-8'))
cenas = e0.get('cenas') or [{"id": i["id"], "start": i["start"], "dur": i["dur"], "texto": i["label"]} for i in e0["items"] if i["type"] == "scene"]
items, out, cnt, cur = [], [], {}, None
for line in src.split('\n'):
    m = re.match(r"S\.(s\d+)=", line)
    if m: cur = m.group(1)
    if cur and ('TX(' in line) and (line.startswith('S.') or line.startswith(' ')) and 'function' not in line:
        def rep(mm):
            k = cnt.get(cur, 0) + 1; cnt[cur] = k; iid = f"{cur}_t{k}"
            items.append({"id": iid, "type": "param", "label": f"Texto {cur} #{k}", "props": {"value": mm.group(1).replace('<br>', '\n')}})
            return f"TX(X('{iid}')"
        line = re.sub(r"TX\('([^']*)'", rep, line)
    if line.startswith('const root='): cur = None
    out.append(line)
src = '\n'.join(out)
src = src.replace("const T = __TIMES__;", "const EDIT = __EDIT__;\nconst ED = Object.fromEntries(EDIT.items.map(i=>[i.id,i]));\nconst X = id => (ED[id]&&!ED[id].hidden ? String(ED[id].props.value) : '').replace(/\n/g,'<br>');\nconst T = Object.fromEntries(EDIT.items.filter(i=>i.type==='scene'&&!i.hidden).map(i=>[i.id,[i.start,i.dur]]));")
src = src.replace('</body>', '<!--__ITEMS__-->\n<!--__ITEMS_SCRIPT__-->\n</body>')
open('template.html', 'w', encoding='utf-8').write(src)
scenes = [{"id": c["id"], "type": "scene", "track": "fundo", "label": c["texto"], "start": c["start"], "dur": c["dur"], "by": "template", "props": {"scene": "local", "params": {}}} for c in cenas]
W = [(5.22, 's3'), (20.98, 's8'), (33.88, 's13'), (45.3, 's17')]
ed = {"version": 1, "name": "07 - METAFORA PERSONAGEM FIXO - Esquema de pirâmide explicado com macacos e bananas",
      "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#ffffff"}, "duration": 60.88, "template": "local", "fonts": {}, "head": "",
      "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
                "extra": [{"id": f"a{i+1}", "src": "sfx/whoosh.wav", "start": round(t - 0.12, 2), "volume": 0.15, "label": "whoosh " + s} for i, (t, s) in enumerate(W)]},
      "tracks": [{"id": "fundo", "name": "Cenas"}, {"id": "textos", "name": "Textos"}],
      "items": scenes + items}
json.dump(ed, open('edit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(scenes), len(items))
