"""Converte vídeos feitos fora do editor (edit.json antigo com 'cenas') em projeto editável (template 'auto').

Marca no HTML da composição cada texto, imagem e clipe com data-ed="eN" (template.ed.html)
e gera os items do edit.json. O build aplica as mudanças do edit.json nesse HTML marcado.
"""
import json
import re
import shutil
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

SKIP = {"script", "style", "head", "title", "meta", "link"}


def _num(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _leaf_text(el):
    if el.name in SKIP or any(p.name in SKIP for p in el.parents if isinstance(p, Tag)):
        return None
    if any(isinstance(c, Tag) and c.name != "br" for c in el.children):
        return None
    txt = el.get_text("\n" if el.find("br") else "").strip()
    return txt if txt and re.search(r"\w", txt) else None


def convert(proj: Path, legacy: dict, norm: dict):
    comp = proj / norm["composition"]
    cdir = comp.parent
    orig = cdir / "index.orig.html"
    if not orig.exists():
        shutil.copy2(comp, orig)
    shutil.copy2(proj / "edit.json", proj / "edit_original.json")
    soup = BeautifulSoup(orig.read_text(encoding="utf-8"), "html.parser")
    body = soup.body or soup
    DUR = norm["duration"]
    cena_t = {}
    for c in legacy.get("cenas") or []:
        m = re.search(r"#([\w-]+)$", str(c.get("src", "")))
        key = c.get("id") or (m.group(1) if m else None)
        if key:
            cena_t[str(key)] = (_num(c.get("start")), _num(c.get("dur"), 1), str(c.get("texto") or ""))
    n = 0
    items = []

    def tag(el):
        nonlocal n
        n += 1
        el["data-ed"] = f"e{n}"
        return f"e{n}"

    def timing_of(el):
        cur = el
        while isinstance(cur, Tag):
            if cur.get("data-start") is not None and cur.get("data-composition-id") != "main":
                return _num(cur["data-start"]), _num(cur.get("data-duration"), DUR)
            if cur.get("id") in cena_t:
                return cena_t[cur["id"]][:2]
            cur = cur.parent
        return None

    for el in body.find_all(True):
        if el.get("data-composition-id") == "main" or el.name in SKIP:
            continue
        if "clip" in (el.get("class") or []) and el.get("data-start") is not None:
            ed = tag(el)
            lab = (el.get_text(" ", strip=True) or Path(el.get("src", "") or el.name).name)[:50]
            items.append({"id": ed, "type": "legacy", "track": "cenas", "by": "template", "label": lab or ed,
                          "start": _num(el["data-start"]), "dur": _num(el.get("data-duration"), 1), "props": {"ed": ed, "clip": True}})
        elif el.get("id") in cena_t:
            s, d, t = cena_t[el["id"]]
            ed = tag(el)
            items.append({"id": ed, "type": "legacy", "track": "cenas", "by": "template", "label": (t or el["id"])[:50],
                          "start": s, "dur": d, "props": {"ed": ed}})
    for el in body.find_all(True):
        txt = _leaf_text(el)
        if not txt:
            continue
        ed = el.get("data-ed") or tag(el)
        tm = timing_of(el)
        if tm:
            items.append({"id": ed + "t", "type": "text", "track": "textos", "by": "template", "label": txt[:40],
                          "start": tm[0], "dur": tm[1], "props": {"ed": ed, "text": txt}})
        else:
            items.append({"id": ed + "t", "type": "param", "label": "Texto: " + txt[:40], "props": {"ed": ed, "value": txt}})
    for el in body.find_all("img"):
        if not el.get("src") or el["src"].startswith("data:"):
            continue
        ed = el.get("data-ed") or tag(el)
        tm = timing_of(el) or (0, DUR)
        items.append({"id": ed + "i", "type": "image", "track": "imagens", "by": "template", "label": Path(el["src"]).name[:40],
                      "start": tm[0], "dur": tm[1],
                      "props": {"ed": ed, "src": (Path(norm["composition"]).parent / el["src"]).as_posix()}})
    mode = "dom"
    if sum(1 for i in items if i["type"] in ("text", "param")) < 3:  # textos gerados por script: modo cru
        items = convert_raw(proj, norm, orig)
        mode = "raw"
    (cdir / "template.ed.html").write_text(str(soup), encoding="utf-8")
    ed = {k: v for k, v in norm.items() if k not in ("items", "tracks", "_legacy")}
    ed["auto_mode"] = mode
    ed.update({"template": "auto", "composition": (Path(norm["composition"]).parent / "template.ed.html").as_posix(),
               "tracks": [{"id": "cenas", "name": "Cenas"}, {"id": "imagens", "name": "Imagens"}, {"id": "textos", "name": "Textos"}],
               "items": items})
    (proj / "edit.json").write_text(json.dumps(ed, ensure_ascii=False, indent=1), encoding="utf-8")
    return ed


def apply(proj: Path, edit: dict, preview: bool):
    tpl = proj / edit["composition"]
    cdir = tpl.parent
    if edit.get("auto_mode") == "raw":
        return apply_raw(proj, edit, cdir / "index.orig.html", cdir / ("_ed_preview.html" if preview else "index.html"))
    soup = BeautifulSoup(tpl.read_text(encoding="utf-8"), "html.parser")
    els = {e["data-ed"]: e for e in soup.find_all(attrs={"data-ed": True})}

    def hide(el, how):
        el["style"] = (el.get("style", "") + ";" + how).lstrip(";")

    def orig_timing(el):  # tempo original herdado do clipe pai (template.ed.html nunca é alterado)
        cur = el.parent
        while isinstance(cur, Tag):
            if cur.get("data-start") is not None and cur.get("data-composition-id") != "main":
                return _num(cur["data-start"]), _num(cur.get("data-duration"), 1)
            cur = cur.parent
        return None

    orig = {k: orig_timing(e) for k, e in els.items()}
    windows = []  # texto/imagem com tempo diferente do herdado -> janela de visibilidade própria
    for it in edit.get("items", []):
        p = it.get("props") or {}
        el = els.get(p.get("ed"))
        if el is None:
            continue
        if it["type"] in ("text", "image") and it.get("start") is not None and "clip" not in (el.get("class") or []):
            o = orig.get(p.get("ed"))
            s, d = _num(it.get("start")), _num(it.get("dur"), 1)
            if o and (abs(s - o[0]) > 0.01 or abs(d - o[1]) > 0.01):
                windows.append([p["ed"], round(s, 3), round(s + d, 3)])
        if it["type"] == "legacy":
            if p.get("clip"):
                el["data-start"] = f"{_num(it.get('start')):.3f}"
                el["data-duration"] = f"{_num(it.get('dur'), 1):.3f}"
            if it.get("hidden"):
                hide(el, "display:none")
        elif it["type"] in ("text", "param"):
            val = str(p.get("text") if it["type"] == "text" else p.get("value", ""))
            el.clear()
            for k, line in enumerate(val.split("\n")):
                if k:
                    el.append(soup.new_tag("br"))
                el.append(NavigableString(line))
            if it.get("hidden"):
                hide(el, "visibility:hidden")
        elif it["type"] == "image":
            src = Path(p.get("src", ""))
            try:
                el["src"] = (proj / src).resolve().relative_to(cdir.resolve()).as_posix()
            except ValueError:  # imagem fora da pasta da composição (ex.: midia/ enviada pelo editor): espelha em hf/m/
                from build_from_edit import Media
                el["src"] = Media(proj, cdir)(src.as_posix())
            if it.get("hidden"):
                hide(el, "visibility:hidden")
    html = str(soup)
    if edit.get("duration"):
        html = re.sub(r'(data-composition-id="main"[^>]*data-duration=")[\d.]+', lambda m: m.group(1) + str(edit["duration"]), html, count=1)
    if windows:
        js = ("<script>(function(){var W=" + json.dumps(windows) + ";function go(){var tl=window.__timelines&&window.__timelines.main;"
              "if(!tl){return false;}W.forEach(function(w){var el=document.querySelector('[data-ed=\"'+w[0]+'\"]');if(!el)return;"
              "if(w[1]>0)tl.set(el,{visibility:'hidden'},0);tl.set(el,{visibility:'inherit'},w[1]);tl.set(el,{visibility:'hidden'},w[2]);});return true;}"
              "if(!go()){window.addEventListener('load',go);}})();</script>")
        html = html.replace("</body>", js + "\n</body>") if "</body>" in html else html + js
    out = cdir / ("_ed_preview.html" if preview else "index.html")
    out.write_text(html, encoding="utf-8")
    return out


# ---------------- modo "texto cru": textos dentro de strings JS (ex.: add('s1',0,7.3,`<div>..</div>`))
RAW = re.compile(r">([^<>{}();=`$\\]{1,200})<")


def raw_matches(src):
    out = []
    for m in RAW.finditer(src):
        t = m.group(1)
        if not re.search(r"[A-Za-zÀ-ú0-9]", t) or not t.strip():
            continue
        out.append(m)
    return out


def convert_raw(proj: Path, norm: dict, orig: Path):
    src = orig.read_text(encoding="utf-8")
    style_spans = [(m.start(), m.end()) for m in re.finditer(r"<style.*?</style>", src, re.S)]
    adds = [(m.start(), m.group(1), _num(m.group(2)), _num(m.group(3)))
            for m in re.finditer(r"add\(\s*['\"]([\w-]+)['\"]\s*,\s*([\d.]+)\s*,\s*([\d.]+)", src)]
    items, seen = [], set()
    for a in adds:
        if a[1] not in seen:
            seen.add(a[1])
            items.append({"id": "cena_" + a[1], "type": "legacy", "track": "cenas", "by": "template", "label": a[1],
                          "start": a[2], "dur": round(a[3] - a[2], 3), "props": {}})
    for k, m in enumerate(raw_matches(src)):
        if any(s <= m.start() < e for s, e in style_spans):
            continue
        prev = [a for a in adds if a[0] < m.start()]
        txt = m.group(1).strip()
        if prev:
            a = prev[-1]
            items.append({"id": f"r{k}", "type": "text", "track": "textos", "by": "template", "label": txt[:40],
                          "start": a[2], "dur": round(a[3] - a[2], 3), "props": {"raw": k, "text": txt}})
        else:
            items.append({"id": f"r{k}", "type": "param", "label": "Texto: " + txt[:40], "props": {"raw": k, "value": txt}})
    return items


def apply_raw(proj: Path, edit: dict, orig: Path, out: Path):
    src = orig.read_text(encoding="utf-8")
    want = {}
    for it in edit.get("items", []):
        p = it.get("props") or {}
        if "raw" in p:
            v = str(p.get("text") if it["type"] == "text" else p.get("value", ""))
            if it.get("hidden"):
                v = ""
            want[int(p["raw"])] = v.replace("<", "&lt;").replace("`", "'").replace("${", "$ {")
    parts, last = [], 0
    for k, m in enumerate(raw_matches(src)):
        if k in want:
            parts.append(src[last:m.start(1)])
            lead = m.group(1)[: len(m.group(1)) - len(m.group(1).lstrip())]
            trail = m.group(1)[len(m.group(1).rstrip()):]
            parts.append(lead + want[k] + trail)
            last = m.end(1)
    parts.append(src[last:])
    html = "".join(parts)
    # cena escondida (modo cru: as animações têm tempo fixo no script, então só dá para esconder)
    hid = [it["id"][5:] for it in edit.get("items", []) if it.get("type") == "legacy" and it.get("hidden") and str(it.get("id", "")).startswith("cena_")]
    if hid:
        css = "<style>" + ",".join(f"#{h}" for h in hid) + "{display:none!important}</style>"
        html = html.replace("</head>", css + "</head>", 1) if "</head>" in html else css + html
    if edit.get("duration"):
        html = re.sub(r'(data-composition-id="main"[^>]*data-duration=")[\d.]+', lambda mm: mm.group(1) + str(edit["duration"]), html, count=1)
    out.write_text(html, encoding="utf-8")
    return out
