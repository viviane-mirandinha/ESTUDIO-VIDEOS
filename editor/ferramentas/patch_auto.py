from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b = ROOT / "build_from_edit.py"
t = b.read_text(encoding="utf-8")


def R(a, c):
    global t
    assert a in t, a[:60]
    t = t.replace(a, c, 1)


R('''def load_edit(proj: Path):
    return normalize(json.loads((Path(proj) / "edit.json").read_text(encoding="utf-8")), Path(proj))''',
  '''def load_edit(proj: Path, convert=True):
    proj = Path(proj)
    raw = json.loads((proj / "edit.json").read_text(encoding="utf-8"))
    ed = normalize(raw, proj)
    if convert and ed.get("template") == "prebuilt" and (proj / ed["composition"]).exists():
        import legacy_auto
        ed = legacy_auto.convert(proj, raw, ed)
    return ed''')
R('''    if tpl == "prebuilt":  # vídeo feito fora do editor: usa a composição como está
        return proj / edit["composition"]''', '''    if tpl == "prebuilt":  # vídeo feito fora do editor: usa a composição como está
        return proj / edit["composition"]
    if tpl == "auto":  # vídeo antigo convertido: aplica as mudanças no HTML marcado
        import legacy_auto
        return legacy_auto.apply(proj, edit, preview=out_dir is not None)''')
b.write_text(t, encoding="utf-8")

s = ROOT / "server.py"
t = s.read_text(encoding="utf-8")
R('if edit.get("template") == "prebuilt":', 'if edit.get("template") in ("prebuilt", "auto"):')
R('if f.suffix == ".html" and (f.parent.name in (".editor_preview", "hf") or f.name == "index.html"):', 'if f.suffix == ".html":')
R('''            try:
                ed = B.normalize(json.loads(e.read_text(encoding="utf-8")), p)
            except Exception:
                ed = {}''', '''            try:
                ed = B.load_edit(p)
            except Exception:
                ed = {}''')
R('''            res.append({"id": pid_of(p), "name": ed.get("name") or p.name,''',
  '''            res.append({"id": pid_of(p), "name": ed.get("name") or p.name, "estilo": estilo_of(ed, p),''')
R('''def edit_duration(ed):''', '''def estilo_of(ed, p: Path):
    if ed.get("estilo"):
        return ed["estilo"]
    parts = [x.strip() for x in str(ed.get("name") or "").split(" - ")]
    if len(parts) >= 3 and parts[0].isdigit():
        return parts[1].title()
    return re.sub(r"^\\d+[-_ ]*", "", p.name).replace("-", " ").title()


def edit_duration(ed):''')
if "\nimport re\n" not in t:
    t = t.replace("import shutil\n", "import re\nimport shutil\n", 1)
s.write_text(t, encoding="utf-8")

j = ROOT / "static" / "app.js"
t = j.read_text(encoding="utf-8")
R('''      <div class="badge ${p.rendered ? "ok" : "no"}">${p.rendered ? "✅ VÍDEO PRONTO" : "⏳ ainda sem vídeo"}</div>
      <div class="nm">${esc(p.name)}</div>
      <div class="meta">${p.w}×${p.h} · ${fmt(p.dur)}<br>${esc(p.folder.split(/[\\\\/]/).pop())}</div>''',
  '''      <div class="badge ${p.rendered ? "ok" : "no"}">${p.rendered ? "✅ VÍDEO PRONTO" : "⏳ ainda sem vídeo"}</div>
      <div class="estilo">🎨 ${esc(p.estilo || "")}</div>
      <div class="nm">${esc(String(p.name).replace(/^\\d+\\s*-\\s*[^-]+-\\s*/, ""))}</div>
      <div class="meta">${p.w}×${p.h} · ${fmt(p.dur)}</div>''')
R('''    <h2 class="grp">📁 ${esc(gr)} <span>''', '''    <h2 class="grp">${gr.includes("TESTE ESTILOS") ? "🎬 Vídeos do YouTube" : "📱 Outros vídeos"} <span>''')
# params ligados à cena selecionada (ex.: s1 -> s1_t1)
R('''    if (it.type === "scene") {''', '''    const rel = items().filter((x) => x.type === "param" && x.id.startsWith(it.id + "_"));
    rel.forEach((x) => (h += field(`edit.items.${items().indexOf(x)}.props.value`, "value", x.props.value, x.label || x.id)));
    if (it.type === "scene") {''')
j.write_text(t, encoding="utf-8")

c = ROOT / "static" / "style.css"
y = c.read_text(encoding="utf-8")
y += "\n.estilo{padding:8px 12px 0;color:var(--ac);font-weight:800;font-size:14px;text-transform:uppercase;letter-spacing:.03em}\n"
c.write_text(y, encoding="utf-8")
print("ok")
