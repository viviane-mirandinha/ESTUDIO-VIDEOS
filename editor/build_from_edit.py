"""build_from_edit.py — gera hf/index.html (HyperFrames) a partir de edit.json e, opcional, renderiza.

Uso:
  python build_from_edit.py <pasta_projeto>             # só gera hf/index.html
  python build_from_edit.py <pasta_projeto> --render    # gera + render + áudio + leve.mp4 + thumb.jpg
Formato: ver FORMATO.md
"""
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
SCENES = TEMPLATES / "scenes"
BLOCOS = TEMPLATES / "blocos"   # ✨ Animações prontas (registry HyperFrames, Apache-2.0) — ver blocos/LICENCAS-TERCEIROS.md
PKG = Path(__file__).resolve().parents[1]   # raiz do ESTUDIO-VIDEOS (package.json com o hyperframes)
HF_BIN = PKG / "node_modules" / ".bin" / ("hyperframes.cmd" if os.name == "nt" else "hyperframes")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
HF_JSON = {
    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
    "media": {"autoProxy": True},
}
TEXT_TYPES = ("text", "caption")


# ---------------------------------------------------------------- util
def esc(s):
    return _html.escape(str(s if s is not None else ""), quote=True)


def num(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def load_edit(proj: Path, convert=True):
    proj = Path(proj)
    raw = json.loads((proj / "edit.json").read_text(encoding="utf-8"))
    ed = normalize(raw, proj)
    if convert and ed.get("template") == "prebuilt" and (proj / ed["composition"]).exists():
        import legacy_auto
        ed = legacy_auto.convert(proj, raw, ed)
    return ed


def normalize(ed, proj: Path):
    """Aceita edit.json antigo (cenas/audio texto/composition) -> formato v1 com template 'prebuilt'."""
    if "items" in ed and isinstance(ed.get("audio", {}), dict):
        return ed
    out = {"version": 1, "canvas": ed.get("canvas") or {"w": 1280, "h": 720, "fps": 30}, "template": "prebuilt", "_legacy": True}
    vids = [f for f in proj.glob("*.mp4") if f.stem.lower() not in ("render_mudo", "silent", "leve", "final")]
    out["name"] = ed.get("name") or (vids[0].stem if vids else proj.name)
    comp = ed.get("composition")
    if not comp and ed.get("hyperframes_project"):
        comp = str(Path(ed["hyperframes_project"]) / "index.html")
    if not comp:
        comp = "hf/index.html"
    cp = Path(comp)
    if cp.is_absolute():
        try:
            cp = cp.relative_to(proj)
        except ValueError:
            pass
    out["composition"] = cp.as_posix()
    a = ed.get("audio")
    out["audio"] = {"voice": {"src": a, "volume": 1.0, "start": 0}} if isinstance(a, str) else (a or {})
    items, ends = [], []
    for n, c in enumerate(ed.get("cenas") or []):
        s, d = num(c.get("start")), num(c.get("dur"), 1)
        ends.append(s + d)
        props = {k: v for k, v in c.items() if k not in ("start", "dur", "id")}
        items.append({"id": str(c.get("id") or f"c{n + 1}"), "type": "legacy", "track": "cenas", "by": "template",
                      "label": str(c.get("texto") or c.get("tipo") or f"cena {n + 1}")[:60], "start": s, "dur": d, "props": props})
    out["items"] = items
    out["tracks"] = [{"id": "cenas", "name": "Cenas"}]
    dur = ed.get("duration")
    if not dur:
        cf = proj / out["composition"]
        if cf.exists():
            m = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"|data-duration="([\d.]+)"[^>]*data-composition-id="main"',
                          cf.read_text(encoding="utf-8", errors="ignore"))
            if m:
                dur = float(m.group(1) or m.group(2))
    out["duration"] = round(float(dur or (max(ends) if ends else 10)), 3)
    return out


def save_edit(proj: Path, edit):
    p = proj / "edit.json"
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


class Media:
    """Espelha mídias do projeto dentro de <out>/m/ (hardlink, senão cópia)."""

    def __init__(self, proj: Path, out: Path):
        self.proj, self.out = proj, out
        self.done = {}

    def __call__(self, src):
        if not src:
            return ""
        if re.match(r"^(https?:|data:)", src):
            return src
        if src in self.done:
            return self.done[src]
        p = Path(src)
        if not p.is_absolute():
            p = self.proj / src
            rel = Path(src)
        else:
            rel = Path("abs") / p.name
        rel_url = "m/" + rel.as_posix()
        dst = self.out / "m" / rel
        if p.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or dst.stat().st_size != p.stat().st_size or dst.stat().st_mtime < p.stat().st_mtime:
                if dst.exists():
                    dst.unlink()
                try:
                    os.link(p, dst)
                except OSError:
                    shutil.copy2(p, dst)
        self.done[src] = rel_url
        return rel_url


def words_of(proj: Path, props):
    if props.get("words"):
        return props["words"]
    f = props.get("words_file")
    if f and (proj / f).exists():
        return json.loads((proj / f).read_text(encoding="utf-8"))
    return []


def caption_groups(words, per=3, gap=0.3):
    groups, g = [], []
    for i, w in enumerate(words):
        g.append(w)
        nx = words[i + 1] if i + 1 < len(words) else None
        if re.search(r"[.,?!;:]$", w["w"]) or len(g) >= per or (nx and nx["s"] - w["e"] > gap) or not nx:
            groups.append(g)
            g = []
    out = []
    for i, g in enumerate(groups):
        s = g[0]["s"] - 0.08
        nxt = groups[i + 1][0]["s"] - 0.08 if i + 1 < len(groups) else None
        e = min(nxt, g[-1]["e"] + 0.7) if nxt is not None else g[-1]["e"] + 0.8
        out.append({"s": round(s, 3), "e": round(e, 3), "w": g})
    return out


# ---------------------------------------------------------------- generic items
def media_fx(p):
    """Efeitos opcionais em foto/vídeo: "blur" (px, fundo desfocado dos cortes 9:16) e "brilho" (0-1, escurecer)."""
    f = []
    if num(p.get("blur")) > 0:
        f.append(f"blur({num(p['blur'])}px)")
    if p.get("brilho") is not None and num(p.get("brilho"), 1) != 1:
        f.append(f"brightness({num(p['brilho'], 1)})")
    if not f:
        return ""
    return f"filter:{' '.join(f)};" + ("transform:scale(1.12);" if num(p.get("blur")) > 0 else "")


def box_style(p, W, H, z):
    if p.get("fill"):
        st = f"left:0;top:0;width:{W}px;height:{H}px;"
    else:
        x, y = num(p.get("x"), W / 2), num(p.get("y"), H / 2)
        st = f"left:{x}px;top:{y}px;transform:translate(-50%,-50%);"
        if p.get("w"):
            st += f"width:{num(p['w'])}px;"
        if p.get("h"):
            st += f"height:{num(p['h'])}px;"
    st += f"z-index:{z};"
    if "opacity" in p:
        st += f"opacity:{num(p['opacity'], 1)};"
    return st


def text_html(p):
    t = esc(p.get("text", ""))
    if p.get("upper"):
        t = t.upper()
    for h in p.get("highlight") or []:
        if h:
            hh = esc(h.upper() if p.get("upper") else h)
            t = t.replace(hh, f'<span class="ed-hl" style="color:{esc(p.get("hl_color", "#ff8a1f"))}">{hh}</span>')
    return t.replace("\n", "<br>")


def text_style(p):
    st = (f"font-size:{num(p.get('size'), 56)}px;color:{p.get('color', '#fff')};"
          f"font-weight:{p.get('weight', 800)};text-align:{p.get('align', 'center')};"
          f"font-family:'{p.get('font', 'Inter')}',Inter,Arial,sans-serif;line-height:{p.get('line', 1.15)};")
    if p.get("bg"):
        st += f"background:{p['bg']};padding:{num(p.get('pad'), 14)}px {num(p.get('pad'), 14) * 1.6}px;border-radius:{num(p.get('radius'), 12)}px;"
    if p.get("stroke"):
        st += f"-webkit-text-stroke:{p.get('stroke_w', 3)}px {p['stroke']};paint-order:stroke fill;"
    if p.get("shadow", True):
        st += "text-shadow:0 3px 14px rgba(0,0,0,.55);"
    if p.get("letter"):
        st += f"letter-spacing:{p['letter']};"
    return st


def scene_fragment(name, it, W, H, media=None):
    f = SCENES / f"{name}.html"
    if not f.exists():
        return f'<div style="color:#f44;font:30px Arial">cena "{esc(name)}" não existe</div>', ""
    src = f.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--params\s*(\{.*?\})\s*-->", src, re.S)
    defaults = json.loads(m.group(1)) if m else {}
    if m:
        src = src[m.end():]
    P = dict(defaults)
    P.update(it.get("props", {}).get("params") or {})
    if media:  # params de mídia (src, src2, img...) relativos ao projeto -> espelha em hf/m/ (também dentro de listas/objetos)
        def _mir(v):
            if isinstance(v, str) and re.search(r"\.(png|jpe?g|webp|gif|mp4|webm|svg)$", v, re.I) and not re.match(r"^(https?:|data:|m/)", v):
                return media(v)
            if isinstance(v, list):
                return [_mir(x) for x in v]
            if isinstance(v, dict):
                return {kk: _mir(x) for kk, x in v.items()}
            return v
        for k, v in list(P.items()):
            P[k] = _mir(v)
    rep = {"{{id}}": it["id"], "{{start}}": str(num(it.get("start"))), "{{dur}}": str(num(it.get("dur"), 1)),
           "{{W}}": str(W), "{{H}}": str(H), "{{json}}": json.dumps(P, ensure_ascii=False)}
    for k, v in rep.items():
        src = src.replace(k, v)
    src = re.sub(r"\{\{p\.(\w+)\}\}", lambda mm: esc(P.get(mm.group(1), "")), src)
    scripts = "\n".join(re.findall(r"<script\b[^>]*>.*?</script>", src, re.S))
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", src, flags=re.S)
    return body, scripts


# ---------------------------------------------------------------- blocos (✨ Animações prontas — registry HyperFrames)
def bloco_meta(name):
    f = BLOCOS / str(name) / "bloco.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    except Exception:
        return None


def _vunits(css, bw, bh):
    for u, base in (("vmin", min(bw, bh)), ("vmax", max(bw, bh)), ("vw", bw), ("vh", bh)):
        css = re.sub(r"(-?\d*\.?\d+)" + u + r"\b", lambda m, b=base: f"{float(m.group(1)) * b / 100:.3f}px", css)
    return css


def _scope_sel(sel, R):
    parts, depth, cur = [], 0, ""
    for ch in sel:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    out = []
    for s in parts:
        s = s.strip()
        if not s:
            continue
        if s in ("html", "body", ":root", "html body", "html, body"):
            out.append(R)
            continue
        s = re.sub(r"^(html|body|:root)\s+(body\s+)?", "", s)
        s = re.sub(r'^\[data-bloco-id(="[^"]*")?\]', R, s)
        out.append(s if s.startswith(R) else f"{R} {s}")
    return ", ".join(out)


def _scope_css(css, R):
    res, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            res.append(css[i:])
            break
        sel = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        inner = css[j + 1:k - 1]
        if re.match(r"@(media|supports|container|layer)\b", sel):
            res.append(f"{sel}{{{_scope_css(inner, R)}}}")
        elif sel.startswith("@"):
            res.append(f"{sel}{{{inner}}}")
        else:
            res.append(f"{_scope_sel(sel, R)}{{{inner}}}")
        i = k
    return "".join(res)


def _copy_bloco_assets(name, out_dir: Path):
    src = BLOCOS / name
    dst = out_dir / "blocos" / name
    for f in src.rglob("*"):
        if f.is_file() and f.name not in ("bloco.json", "thumb.jpg", "thumb.png") and f.suffix != ".html":
            d = dst / f.relative_to(src)
            if not d.exists() or d.stat().st_size != f.stat().st_size:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, d)


def _limpa_txt(v):
    return (str(v).replace("\\", "/").replace('"', "”").replace("'", "’").replace("<", "‹").replace(">", "›")
            .replace("\n", " ").replace("\r", " "))


def bloco_fragment(it, W, H, out_dir, n, z):
    """Embute um bloco do registry (templates/blocos/<nome>/) dentro da composição principal:
    ids com prefixo, CSS com escopo, scripts com document/window "sombra" e a timeline do bloco
    aninhada na timeline principal em it.start. Retorna (html, css, js)."""
    p = it.get("props", {})
    name = re.sub(r"[^\w.-]", "", str(p.get("bloco", "")))
    meta = bloco_meta(name)
    f = BLOCOS / name / f"{name}.html"
    iid = it["id"]
    s, d = num(it.get("start")), max(0.04, num(it.get("dur"), 1))
    timing = f'class="clip" data-start="{s:.3f}" data-duration="{d:.3f}" data-track-index="{n + 1}"'
    if not meta or not f.exists():
        return (f'<div id="{iid}_box" class="ed-box" style="left:0;top:0;width:{W}px;height:{H}px;z-index:{z}"><div id="{iid}" {timing} '
                f'style="color:#f44;font:30px Arial;padding:20px">animação "{esc(name)}" não existe</div></div>'), "", ""
    src = f.read_text(encoding="utf-8")
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    # textos trocados pelo usuário (lista [{de, para}])
    for tr in p.get("textos") or []:
        de, para = str(tr.get("de", "")), tr.get("para")
        if de and para is not None and str(para) != de:
            pat = r"\s+".join(re.escape(w) for w in de.split())
            src = re.sub(pat, lambda m, v=_limpa_txt(para): v, src)
    src = src.replace("data-composition-id", "data-bloco-id")
    bw, bh = int(num(meta.get("width"), 1920)), int(num(meta.get("height"), 1080))
    P = f"{iid}__"
    body = src.split("<body", 1)[-1]
    body = body[body.find(">") + 1:] if ">" in body else body
    body = body.split("</body>")[0]
    head = src.split("<body", 1)[0]
    styles = re.findall(r"<style\b[^>]*>(.*?)</style>", head + body, flags=re.S | re.I)
    ext = [m for m in re.findall(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>\s*</script>', head + body, flags=re.I)
           if not re.search(r"/gsap(@[\d.]+)?/dist/gsap(\.min)?\.js$", m)]
    scripts = [m for a, m in re.findall(r"<script\b([^>]*)>(.*?)</script>", body, flags=re.S | re.I) if "src=" not in a]
    html = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S | re.I)
    # raiz do bloco
    m = re.search(r'<(\w+)([^>]*\bdata-bloco-id="[^"]*"[^>]*)>', html)
    if m:
        attrs = m.group(2)
        attrs = re.sub(r'\sdata-start="[^"]*"', "", attrs)
        attrs = re.sub(r'\sdata-track-index="[^"]*"', "", attrs)
        attrs = re.sub(r'\sdata-duration="[^"]*"', f' data-duration="{d:.3f}"', attrs)
        attrs = re.sub(r'\bclass="([^"]*)\bclip\b([^"]*)"', r'class="\1\2"', attrs)
        if not re.search(r'(?<![\w-])id="', attrs):
            attrs += ' id="root"'
        html = html[:m.start()] + f"<{m.group(1)}{attrs}>" + html[m.end():]
        root_id = re.search(r'(?<![\w-])id="([^"]+)"', attrs).group(1)
    else:
        html = f'<div id="root">{html}</div>'
        root_id = "root"
    ids = sorted(set(re.findall(r'(?<![\w-])id="([^"]+)"', html + "\n".join(scripts))), key=len, reverse=True)
    ids = [i for i in ids if re.match(r"^[\w-]+$", i)]

    def fix_ids(t, attr=True):
        for i in ids:
            t = re.sub(r"#" + re.escape(i) + r"(?![\w-])", "#" + P + i, t)
            if attr:
                t = re.sub(r'((?<![\w-])(?:id|for|aria-labelledby|aria-describedby)=")' + re.escape(i) + '"', r"\g<1>" + P + i + '"', t)
        return t

    html, scripts = fix_ids(html), [fix_ids(sc, attr=False) for sc in scripts]
    R = f"#{P}{root_id}"
    css = _scope_css(_vunits(fix_ids(re.sub(r"/\*.*?\*/", "", "\n".join(styles), flags=re.S), attr=False), bw, bh), R)
    # caminhos dos arquivos do bloco (fontes/scripts) -> hf/blocos/<nome>/
    base = f"blocos/{name}/"
    fixp = lambda t: re.sub(r'''((?:src|href)=["']|url\(["']?)(?:\./)?(assets/)''', r"\1" + base + r"\2", t)
    css, html = fixp(css), fixp(html)
    ext = [base + e[2:] if e.startswith("./") else (base + e if not re.match(r"^(https?:|/)", e) else e) for e in ext]
    _copy_bloco_assets(name, out_dir)
    # clipes internos: tempo relativo ao bloco -> absoluto
    html = re.sub(r'\bdata-start="([\d.]+)"', lambda mm: f'data-start="{s + float(mm.group(1)):.3f}"', html)
    html = re.sub(r'\bdata-track-index="(\d+)"', lambda mm: f'data-track-index="{1000 + n * 20 + int(mm.group(1))}"', html)
    html = re.sub(r'\bdata-composition-variables=\'[^\']*\'', "", html)
    # tamanho/posição: o bloco é desenhado em bw×bh e escalado para caber no vídeo
    fit = max if p.get("fit") == "cover" else min
    sc = fit(W / bw, H / bh) * num(p.get("scale"), 1)
    cx, cy = num(p.get("x"), W / 2), num(p.get("y"), H / 2)
    vw, vh = bw * sc, bh * sc
    VARS = {v["id"]: v.get("default") for v in meta.get("variables") or [] if "id" in v}
    VARS.update(p.get("vars") or {})
    speed = num(p.get("speed"), 1) or 1
    out_h = (f'<div id="{iid}_box" class="ed-box" style="left:{cx - vw / 2:.2f}px;top:{cy - vh / 2:.2f}px;width:{vw:.2f}px;height:{vh:.2f}px;z-index:{z}">'
             f'<div id="{iid}" {timing} style="width:100%;height:100%;position:relative;overflow:hidden">'
             f'<div id="{iid}_sc" style="position:absolute;left:0;top:0;width:{bw}px;height:{bh}px;transform:scale({sc:.5f});transform-origin:0 0">'
             + "".join(f'<script src="{esc(e)}"></script>' for e in ext) + html + "</div></div></div>")
    css += f"{R}{{position:relative;width:{bw}px;height:{bh}px;overflow:hidden}}"
    code = "\n;\n".join(scripts).replace("</script", "<\\/script")
    js = ("(function(){var R=document.getElementById(%s);if(!R)return;var P=%s,IDS=%s,VARS=%s,LT={},S=%s,SPD=%s;"
          "function fx(s){return typeof s!=='string'?s:s.replace(/#([\\w-]+)/g,function(m,i){return IDS.indexOf(i)>=0?'#'+P+i:m;});}"
          "var SD=new Proxy(document,{get:function(t,k){"
          "if(k==='getElementById')return function(i){return t.getElementById(P+i)||t.getElementById(i);};"
          "if(k==='querySelector')return function(s){s=fx(s);try{if(R.matches(s))return R;}catch(e){}return R.querySelector(s);};"
          "if(k==='querySelectorAll')return function(s){return R.querySelectorAll(fx(s));};"
          "if(k==='body'||k==='documentElement')return R;var v=t[k];return typeof v==='function'?v.bind(t):v;}});"
          "var HFV={getVariables:function(){return Object.assign({},VARS);}};"
          "var SW=new Proxy(window,{get:function(t,k){if(k==='__timelines')return LT;if(k==='__hyperframes')return HFV;"
          "if(k==='__hfVariables')return VARS;if(k==='document')return SD;if(k==='window'||k==='self'||k==='globalThis')return SW;"
          "var v=t[k];return (typeof v==='function'&&!v.prototype)?v.bind(t):v;},"
          "set:function(t,k,v){if(k!=='__timelines')t[k]=v;return true;}});"
          "try{(function(window,document,self,globalThis){\n%s\n}).call(SW,SW,SD,SW,SW);}catch(e){console.error('bloco %s:',e);}"
          "Object.keys(LT).forEach(function(k){var c=LT[k];if(!c||typeof c.paused!=='function')return;c.paused(false);if(SPD!==1)c.timeScale(SPD);tl.add(c,S);});"
          "})();") % (json.dumps(P + root_id), json.dumps(P), json.dumps(ids), json.dumps(VARS, ensure_ascii=False).replace("</", "<\\/"),
                      f"{s:.3f}", speed, code, name)
    return out_h, css, js


def anim_js(it, sel):
    s, d = num(it.get("start")), num(it.get("dur"), 1)
    e = s + d
    js = []
    a_in, a_out = it.get("in", "none"), it.get("out", "none")
    fin = {"fade": "{opacity:0}", "slide_up": "{opacity:0,y:50}", "slide_left": "{opacity:0,x:80}",
           "pop": "{opacity:0,scale:.6}", "zoom": "{opacity:0,scale:1.18}"}
    if a_in in fin:
        ease = "back.out(1.7)" if a_in == "pop" else "power2.out"
        js.append(f'tl.fromTo("{sel}",{fin[a_in]},{{opacity:1,x:0,y:0,scale:1,duration:{min(.45, d / 2):.3f},ease:"{ease}",immediateRender:false}},{s:.3f});')
        if s > 0:  # em s == 0 o set(0) ficaria por cima do fromTo(0) e o item sumia
            js.append(f'tl.set("{sel}",{fin[a_in]},0);')
    elif a_in == "type":
        js.append(f'(function(){{const sp=document.querySelectorAll("{sel} .ed-ch");gsap.set(sp,{{opacity:0}});'
                  f'sp.forEach((c,i)=>tl.set(c,{{opacity:1}},{s:.3f}+i*{min(0.05, d * 0.5 / 60):.4f}));}})();')
    fout = {"fade": "{opacity:0}", "slide_up": "{opacity:0,y:-40}", "slide_left": "{opacity:0,x:-80}",
            "pop": "{opacity:0,scale:.7}", "zoom": "{opacity:0,scale:1.15}"}
    if a_out in fout:
        od = min(.35, d / 3)
        js.append(f'tl.to("{sel}",{{...{fout[a_out]},duration:{od:.3f},ease:"power2.in"}},{e - od:.3f});')
    return js


def motion_js(it, sel):
    p = it.get("props", {})
    mo = p.get("motion", "none")
    if not mo or mo == "none":
        return []
    s, d = num(it.get("start")), num(it.get("dur"), 1)
    a = num(p.get("motion_amount"), 0.08)
    frm, to = {
        "zoom_in": (f"{{scale:1}}", f"{{scale:{1 + a}}}"),
        "zoom_out": (f"{{scale:{1 + a}}}", "{scale:1}"),
        "pan_left": (f"{{scale:{1 + a},xPercent:{a * 50}}}", f"{{scale:{1 + a},xPercent:{-a * 50}}}"),
        "pan_right": (f"{{scale:{1 + a},xPercent:{-a * 50}}}", f"{{scale:{1 + a},xPercent:{a * 50}}}"),
        "pan_up": (f"{{scale:{1 + a},yPercent:{a * 50}}}", f"{{scale:{1 + a},yPercent:{-a * 50}}}"),
        "pan_down": (f"{{scale:{1 + a},yPercent:{-a * 50}}}", f"{{scale:{1 + a},yPercent:{a * 50}}}"),
    }.get(mo, (None, None))
    if not frm:
        return []
    out = [f'tl.fromTo("{sel}",{frm},{{...{to},duration:{d:.3f},ease:"none",immediateRender:false}},{s:.3f});']
    if s > 0:
        out.append(f'tl.set("{sel}",{frm},0);')
    return out


def render_items(edit, proj: Path, media: Media, skip_by_template=True, hide_text=False):
    """Retorna (html, css, js) dos itens genéricos."""
    W, H = int(edit["canvas"]["w"]), int(edit["canvas"]["h"])
    order = {t["id"]: i for i, t in enumerate(edit.get("tracks", []))}
    items = [it for it in edit.get("items", []) if it.get("type") != "param"]
    items.sort(key=lambda it: (order.get(it.get("track"), 99), num(it.get("start"))))
    out_h, out_css, out_js = [], [], []
    for n, it in enumerate(items):
        if skip_by_template and it.get("by") == "template":
            continue
        if it.get("hidden") or (hide_text and it.get("type") in TEXT_TYPES):
            continue
        typ, p, iid = it.get("type"), it.get("props", {}), it["id"]
        s, d = num(it.get("start")), max(0.04, num(it.get("dur"), 1))
        z = 10 + order.get(it.get("track"), 50) * 10 + 1
        timing = f'class="clip" data-start="{s:.3f}" data-duration="{d:.3f}" data-track-index="{n + 1}"'
        box = f'<div id="{iid}_box" class="ed-box" style="{box_style(p, W, H, z)}">'
        mv_open, mv_close = f'<div id="{iid}_mv" class="ed-mv">', "</div>"
        if typ == "text":
            inner = text_html(p)
            if it.get("in") == "type":
                inner = "".join(f'<span class="ed-ch">{c}</span>' if c != " " else " " for c in _html.unescape(inner))
            out_h.append(f'{box}<div id="{iid}" {timing} style="{text_style(p)}">{inner}</div></div>')
        elif typ == "image":
            fit = p.get("fit", "cover")
            fx = media_fx(p)
            rad = f"border-radius:{num(p.get('radius'))}px;" if p.get("radius") else ""
            out_h.append(f'{box}{mv_open}<img id="{iid}" {timing} src="{esc(media(p.get("src")))}" '
                         f'style="width:100%;height:100%;object-fit:{fit};{rad}{fx}" />{mv_close}</div>')
        elif typ == "video":
            fit = p.get("fit", "cover")
            fx = media_fx(p)
            extra = f' data-media-start="{num(p.get("trim")):.3f}"' if p.get("trim") else ""
            if p.get("speed") and num(p.get("speed"), 1) != 1:
                extra += f' data-playback-rate="{num(p["speed"], 1)}"'
            out_h.append(f'{box}{mv_open}<video id="{iid}" {timing}{extra} src="{esc(media(p.get("src")))}" muted playsinline '
                         f'style="width:100%;height:100%;object-fit:{fit};{fx}"></video>{mv_close}</div>')
        elif typ == "caption":
            groups = caption_groups(words_of(proj, p), int(p.get("per_group", 3)))
            groups = [g for g in groups if g["e"] > s and g["s"] < s + d]
            kws = [k.lower() for k in p.get("keywords") or []]
            pp = dict(p)
            pp.setdefault("shadow", True)
            parts = []
            for gi, g in enumerate(groups):
                sp = []
                for wi, w in enumerate(g["w"]):
                    k = any(kk in w["w"].lower() for kk in kws)
                    sp.append(f'<span id="{iid}_g{gi}w{wi}" class="ed-w{" ed-k" if k else ""}">{esc(w["w"])}</span>')
                parts.append(f'<div id="{iid}_g{gi}" class="ed-cg" style="opacity:0">{" ".join(sp)}</div>')
                out_js.append(f'tl.set("#{iid}_g{gi}",{{opacity:1}},{max(0, g["s"]):.3f});tl.set("#{iid}_g{gi}",{{opacity:0}},{g["e"]:.3f});')
                for wi, w in enumerate(g["w"]):
                    out_js.append(f'tl.set("#{iid}_g{gi}w{wi}",{{className:"ed-w on{" ed-k" if any(kk in w["w"].lower() for kk in kws) else ""}"}},{max(0, w["s"] - 0.04):.3f});')
            st = text_style(pp)
            st = re.sub(r"background:[^;]*;padding:[^;]*;border-radius:[^;]*;", "", st)
            if p.get("upper"):
                st += "text-transform:uppercase;"
            out_css.append(f'#{iid} .ed-cg{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);white-space:nowrap;'
                           f'{"background:" + p["bg"] + ";padding:10px 26px;border-radius:16px;" if p.get("bg") else ""}}}'
                           f'#{iid} .ed-w{{color:{p.get("dim", "#7b7d85")}}} #{iid} .ed-w.on{{color:{p.get("color", "#fff")}}}'
                           f'#{iid} .ed-w.ed-k.on{{color:{p.get("hl_color", "#ffd400")}}}')
            out_h.append(f'{box.replace("transform:translate(-50%,-50%);", "")}<div id="{iid}" {timing} style="{st}">{"".join(parts)}</div></div>')
        elif typ == "html":
            out_css.append(p.get("css", ""))
            out_h.append(f'{box}<div id="{iid}" {timing} style="width:100%;height:100%">{p.get("html", "")}</div></div>')
        elif typ == "scene":
            body, scr = scene_fragment(p.get("scene", ""), it, W, H, media)
            pp = dict(p)
            pp.setdefault("fill", True)
            out_h.append(f'<div id="{iid}_box" class="ed-box" style="{box_style(pp, W, H, z)}"><div id="{iid}_clip" {timing} '
                         f'style="width:100%;height:100%;position:relative">{body}</div></div>')
            out_js.append(scr.replace("<script>", "").replace("</script>", "") if scr else "")
            continue
        elif typ == "bloco":
            bh_, bc_, bj_ = bloco_fragment(it, W, H, media.out, n, z)
            out_h.append(bh_)
            out_css.append(bc_)
            out_js.append(bj_)
            out_js += anim_js(it, f"#{iid}_box")
            continue
        else:
            continue
        out_js += anim_js(it, f"#{iid}_box")
        if typ in ("image", "video"):
            out_js += motion_js(it, f"#{iid}_mv")
    css = (".ed-box{position:absolute;overflow:visible}.ed-mv{width:100%;height:100%;overflow:hidden}"
           ".ed-box>.clip{position:static;inset:auto}"  # composições antigas têm .clip{position:absolute;inset:0}

           ".ed-box img,.ed-box video{display:block}" + "".join(out_css))
    js = ("<script>(function(){const tl=window.__timelines&&window.__timelines.main;if(!tl)return;\n"
          + "\n".join(out_js) + "\n})();</script>")
    return "\n".join(out_h), css, js


def font_css(edit, media):
    out = ""
    for fam, path in (edit.get("fonts") or {}).items():
        out += f"@font-face{{font-family:'{fam}';src:url('{media(path)}');font-weight:100 900;}}"
    return out


# ---------------------------------------------------------------- build
def build(proj, out_dir=None, hide_text=False, edit=None):
    proj = Path(proj).resolve()
    edit = edit if edit is not None else load_edit(proj)
    out = Path(out_dir) if out_dir else proj / "hf"
    out.mkdir(parents=True, exist_ok=True)
    if not (out / "hyperframes.json").exists():
        (out / "hyperframes.json").write_text(json.dumps(HF_JSON, indent=2), encoding="utf-8")
    media = Media(proj, out)
    cv = edit["canvas"]
    W, H, FPS = int(cv["w"]), int(cv["h"]), int(cv.get("fps", 30))
    DUR = round(num(edit.get("duration"), 10), 3)
    if edit.get("regras"):   # guarda de densidade: esconde o excesso de gráfico (em memória, não grava)
        try:
            import guarda_densidade
            edit = guarda_densidade.filtrar_para_render(edit)
        except Exception:
            pass
    if hide_text:
        edit = json.loads(json.dumps(edit))
        for it in edit["items"]:
            if it.get("type") in TEXT_TYPES:
                it["hidden"] = True
    tpl = edit.get("template", "generic")
    if tpl == "prebuilt":  # vídeo feito fora do editor: usa a composição como está
        return proj / edit["composition"]
    if tpl == "auto":  # vídeo antigo convertido: aplica as mudanças no HTML marcado
        import legacy_auto
        f = legacy_auto.apply(proj, edit, preview=out_dir is not None)
        # itens novos do editor (+ Texto, + Foto…) entram por cima da composição antiga
        items_h, items_css, items_js = render_items(edit, proj, Media(proj, f.parent), hide_text=hide_text)
        if items_h.strip():
            extra = (f"<style>{items_css}</style>\n<div id=\"ed_extra\">{items_h}</div>\n"
                     "<script>(function(){var r=document.querySelector('[data-composition-id=\"main\"]'),x=document.getElementById('ed_extra');"
                     "if(r&&x){while(x.firstChild)r.appendChild(x.firstChild);x.remove();}})();</script>\n" + items_js)
            page = f.read_text(encoding="utf-8")
            page = page.replace("</body>", extra + "\n</body>", 1) if "</body>" in page else page + extra
            f.write_text(page, encoding="utf-8")
        return f
    items_h, items_css, items_js = render_items(edit, proj, media, hide_text=hide_text)
    fonts = font_css(edit, media)
    if tpl == "generic":
        page = f"""<!doctype html>
<html lang="pt"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="{GSAP}"></script>
{edit.get("head", "")}
<style>
{fonts}
html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:{cv.get("bg", "#000")};}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{cv.get("bg", "#000")};font-family:Inter,Arial,sans-serif;color:#fff;}}
{items_css}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{items_h}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused:true}});
tl.to({{v:0}},{{v:1,duration:{DUR},ease:"none"}},0);
window.__timelines["main"] = tl;
</script>
{items_js}
</body></html>
"""
    else:
        tf = proj / "template.html" if tpl == "local" else TEMPLATES / f"{tpl}.html"
        page = tf.read_text(encoding="utf-8")
        # media referenciada no template: src="arquivo" relativo ao projeto -> espelha
        for mm in set(re.findall(r'''(?:src|href)=["']([^"':]+\.(?:png|jpe?g|webp|gif|mp4|webm|mov|svg|ttf|otf|woff2?))["']''', page)):
            media(mm)
        for mm in set(re.findall(r'''url\(['"]?([^'")]+\.(?:ttf|otf|woff2?|png|jpe?g|webp))['"]?\)''', page)):
            media(mm)
        page = re.sub(r'''((?:src|href)=["'])(?!https?:|data:|m/)([^"':]+\.(?:png|jpe?g|webp|gif|mp4|webm|mov|svg|ttf|otf|woff2?)["'])''', r"\1m/\2", page)
        page = re.sub(r'''(url\(['"]?)(?!https?:|data:|m/)([^'")]+\.(?:ttf|otf|woff2?|png|jpe?g|webp))''', r"\1m/\2", page)
        ed_js = json.dumps(edit, ensure_ascii=False).replace("</", "<\\/")
        page = (page.replace("__EDIT__", ed_js).replace("__DUR__", str(DUR)).replace("__W__", str(W))
                .replace("__H__", str(H)).replace("__FPS__", str(FPS)))
        if "<!--__ITEMS__-->" in page:
            page = page.replace("<!--__ITEMS__-->", items_h)
        elif items_h.strip():  # template sem marcador: itens novos entram no fim e são movidos para dentro da composição
            page = page.replace("</body>", f'<div id="ed_extra">{items_h}</div>\n'
                                "<script>(function(){var r=document.querySelector('[data-composition-id=\"main\"]'),x=document.getElementById('ed_extra');"
                                "if(r&&x){while(x.firstChild)r.appendChild(x.firstChild);x.remove();}})();</script>\n</body>", 1)
        page = page.replace("</style>", fonts + items_css + "</style>", 1)
        if "<!--__ITEMS_SCRIPT__-->" in page:
            page = page.replace("<!--__ITEMS_SCRIPT__-->", items_js)
        else:
            page = page.replace("</body>", items_js + "\n</body>")
    (out / "index.html").write_text(page, encoding="utf-8")
    return out / "index.html"


# ---------------------------------------------------------------- render
class RenderFalhou(RuntimeError):
    def __init__(self, msg, head, tail):
        super().__init__(msg)
        self.head, self.tail = head, tail


def run(cmd, cwd=None, on_line=None, env=None):
    """Roda e guarda o COMEÇO (40 linhas) e o FIM (40 linhas) da saída — o erro de verdade costuma estar no começo."""
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", bufsize=1, env=env,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    buf, head, tail = "", [], []
    while True:
        ch = p.stdout.read(1)
        if not ch:
            break
        if ch in "\r\n":
            if buf.strip():
                if len(head) < 40:
                    head.append(buf)
                tail = (tail + [buf])[-40:]
                if on_line:
                    on_line(buf)
            buf = ""
        else:
            buf += ch
    p.wait()
    if p.returncode != 0:
        raise RenderFalhou("Falhou: " + " ".join(map(str, cmd[:3])) + "\n" + "\n".join(tail[-15:]), head, tail)
    return tail


RENDER_TENTATIVAS = 8


def _tem_nvidia():
    try:
        return subprocess.run(["nvidia-smi", "-L"], capture_output=True, timeout=10,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).returncode == 0
    except Exception:
        return False


def _hf_opcoes():
    """Flags que ESTA versão do HyperFrames aceita (lê o --help uma vez; versão antiga não tem --resume)."""
    if _hf_opcoes.cache is None:
        try:
            h = subprocess.run([str(HF_BIN), "render", "--help"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        except Exception:
            h = ""
        _hf_opcoes.cache = {f for f in ("--resume", "--gpu", "--low-memory-mode", "--workers", "--protocol-timeout", "--player-ready-timeout",
                                        "--browser-timeout") if f in (h or "")}
    return _hf_opcoes.cache


_hf_opcoes.cache = None


def hf_render(hf_dir: Path, out_mp4: Path, progress=None, lo=0, hi=80):
    """Render HyperFrames com captura segmentada e até 8 tentativas (o Chrome às vezes cai no meio, ~frame 300-450,
    em PC com pouca RAM livre). A cada queda tenta de novo com um perfil mais leve; se --resume existir, continua de onde parou.
    Se todas falharem, grava render-erro.log (começo + fim da saída de cada tentativa) na pasta do projeto."""
    proj = hf_dir.parent
    opc = _hf_opcoes()
    gpu = "--gpu" in opc and _tem_nvidia()
    env = {**os.environ, "HF_SEGMENTED_CAPTURE": "true"}
    log_erros = []
    for tent in range(1, RENDER_TENTATIVAS + 1):
        def on_line(line, tent=tent):
            m = re.search(r"(\d{1,3})%", line)
            if m and progress:
                extra = f" (tentativa {tent}/{RENDER_TENTATIVAS})" if tent > 1 else ""
                progress(lo + (hi - lo) * int(m.group(1)) / 100, "Desenhando os quadros do vídeo…" + extra)
        cmd = [str(HF_BIN), "render", str(hf_dir), "-o", str(out_mp4), "-q", "standard", "--sdr"]
        if gpu and tent <= 3:
            cmd.append("--gpu")
        if "--resume" in opc and tent > 1:
            cmd.append("--resume")
        if tent >= 2:   # perfil mais leve depois da 1ª queda
            if "--workers" in opc:
                cmd += ["--workers", "2" if tent == 2 else "1"]
            if "--protocol-timeout" in opc:
                cmd += ["--protocol-timeout", "600000"]
            if "--player-ready-timeout" in opc:
                cmd += ["--player-ready-timeout", "120000"]
            if "--browser-timeout" in opc:
                cmd += ["--browser-timeout", "180"]
        if tent >= 4 and "--low-memory-mode" in opc:
            cmd.append("--low-memory-mode")
        try:
            run(cmd, cwd=str(proj), on_line=on_line, env=env)
            if log_erros:   # deu certo depois de cair: deixa registrado
                (proj / "render-erro.log").write_text(f"Render OK na tentativa {tent}/{RENDER_TENTATIVAS} depois de {len(log_erros)} queda(s).\n\n"
                                                      + "\n\n".join(log_erros), encoding="utf-8")
            return
        except RenderFalhou as e:
            log_erros.append(f"===== tentativa {tent}/{RENDER_TENTATIVAS} · {' '.join(cmd[4:])}\n--- começo da saída (40 linhas)\n"
                             + "\n".join(e.head) + "\n--- fim da saída (40 linhas)\n" + "\n".join(e.tail))
            if tent == RENDER_TENTATIVAS:
                f = proj / "render-erro.log"
                f.write_text("\n\n".join(log_erros), encoding="utf-8")
                print(f"RENDER_ERRO_LOG: {f}", flush=True)
                raise RuntimeError(f"O render caiu {RENDER_TENTATIVAS} vezes. Detalhes em render-erro.log.\n--- começo ---\n"
                                   + "\n".join(e.head) + "\n--- fim ---\n" + "\n".join(e.tail))
            if progress:
                progress(lo, f"O render caiu — tentando de novo ({tent + 1}/{RENDER_TENTATIVAS})…")
            import time as _t
            _t.sleep(min(30, 5 * tent))


def audio_inputs(edit, proj: Path):
    """Lista de (path, start, volume, kind, extra) para mix."""
    def P(src):
        p = Path(src)
        return p if p.is_absolute() else proj / src
    a = edit.get("audio") or {}
    res = []
    v = a.get("voice")
    if v and v.get("src") and P(v["src"]).exists() and not v.get("mute"):
        res.append((P(v["src"]), num(v.get("start")), num(v.get("volume"), 1), "voice", v))
    m = a.get("music")
    if m and m.get("src") and P(m["src"]).exists() and not m.get("mute"):
        res.append((P(m["src"]), num(m.get("start")), num(m.get("volume"), 0.12), "music", m))
    for x in a.get("extra") or []:
        if x.get("src") and P(x["src"]).exists() and not x.get("mute"):
            res.append((P(x["src"]), num(x.get("start")), num(x.get("volume"), 1), "extra", x))
    for it in edit.get("items", []):
        p = it.get("props", {})
        if it.get("type") == "video" and num(p.get("volume")) > 0 and not it.get("hidden") and P(p.get("src", "")).exists():
            res.append((P(p["src"]), num(it.get("start")), num(p["volume"]), "clip",
                        {"trim": num(p.get("trim")), "dur": num(it.get("dur"), 1)}))
    return res


def mix_audio(edit, proj: Path, video_in: Path, out_mp4: Path):
    DUR = num(edit.get("duration"), 10)
    ins = audio_inputs(edit, proj)
    if not ins:
        shutil.copy2(video_in, out_mp4)
        return
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video_in)]
    filt, labels, n = [], [], 1
    voice_idx = None
    for path, start, vol, kind, x in ins:
        if kind == "music":
            cmd += ["-stream_loop", "-1"]
        cmd += ["-i", str(path)]
        ms = int(start * 1000)
        chain = f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo"
        if kind == "clip":
            chain += f",atrim={x['trim']:.3f}:{x['trim'] + x['dur']:.3f},asetpts=PTS-STARTPTS"
        if kind == "music":
            chain += f",atrim=0:{max(0.1, DUR - start):.3f}"
            fo = num(x.get("fade_out"), 2)
            if fo > 0:
                chain += f",afade=t=out:st={max(0, DUR - start - fo):.3f}:d={fo:.3f}"
        chain += f",volume={vol:.3f},adelay={ms}|{ms}"
        if kind == "voice":
            voice_idx = len(labels)
        filt.append(chain + f"[a{n}]")
        labels.append((f"a{n}", kind, x))
        n += 1
    # ducking: segunda leitura da voz como sidechain (evita asplit multi-ramo)
    mus = [l for l in labels if l[1] == "music" and l[2].get("duck", True)]
    if mus and voice_idx is not None:
        vpath, vstart = ins[voice_idx][0], ins[voice_idx][1]
        cmd += ["-i", str(vpath)]
        ms = int(vstart * 1000)
        filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[sc]")
        ml = mus[0][0]
        ratio = max(2.0, min(20.0, num(mus[0][2].get("duck_ratio"), 5)))   # música do pedido: 6 (baixinha) / 10 (presente) — abaixa mais quando a voz fala
        filt.append(f"[{ml}][sc]sidechaincompress=threshold=0.02:ratio={ratio:.1f}:attack=20:release=600[{ml}d]")
        labels = [((l[0] + "d") if l[0] == ml else l[0], l[1], l[2]) for l in labels]
        n += 1
    mix = "".join(f"[{l[0]}]" for l in labels)
    filt.append(f"{mix}amix=inputs={len(labels)}:normalize=0:duration=longest,apad,atrim=0:{DUR:.3f}[aout]")
    cmd += ["-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{DUR:.3f}", str(out_mp4)]
    run(cmd)


def marca_dagua_texto(edit, proj):
    """Marca d'água DESTE vídeo: campo "marca_dagua" do edit.json ou arquivo marca_dagua.txt na pasta. Vazio = sem marca."""
    if edit.get("sem_marca"):
        return ""
    t = str(edit.get("marca_dagua") or "").strip()
    if not t:
        try:
            t = (Path(proj) / "marca_dagua.txt").read_text(encoding="utf-8-sig").strip()
        except Exception:
            t = ""
    return t


def apply_watermark(video: Path, texto: str):
    """Escreve o texto pequeno e discreto no vídeo, trocando de lado a cada 8 s. Se falhar, mantém o vídeo como está."""
    tmp_txt = video.with_name("_marca.txt")
    tmp_out = video.with_name("_com_marca.mp4")
    try:
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                             "-of", "csv=p=0", str(video)], capture_output=True, text=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        w, h = [int(x) for x in pr.stdout.strip().split(",")[:2]]
        tmp_txt.write_text(texto, encoding="utf-8")
        fonte = next((f for f in (r"C:/Windows/Fonts/segoeuib.ttf", r"C:/Windows/Fonts/arialbd.ttf",
                                  "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
                      if Path(f).exists()), "")
        tam = max(18, round(min(w, h) / 32))
        m = round(min(w, h) * 0.05)
        y = f"{round(h * 0.12)}" if h > w else f"h-text_h-{round(h * 0.05)}"
        x = rf"if(lt(mod(t\,16)\,8)\,w-text_w-{m}\,{m})"
        f_esc = fonte.replace(":", r"\:")
        tf = str(tmp_txt).replace("\\", "/").replace(":", r"\:")
        dt = (f"drawtext=textfile='{tf}':{'fontfile=' + chr(39) + f_esc + chr(39) + ':' if fonte else ''}fontsize={tam}:"
              f"fontcolor=white@0.5:shadowcolor=black@0.45:shadowx=2:shadowy=2:x={x}:y={y}")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", dt, "-c:v", "libx264", "-preset", "fast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(tmp_out)])
        if tmp_out.exists() and tmp_out.stat().st_size > 10000:
            shutil.move(str(tmp_out), str(video))
    except Exception as e:
        print(f"[aviso] marca d'água não aplicada: {str(e)[-200:]}", flush=True)
    finally:
        for t in (tmp_txt, tmp_out):
            try:
                t.unlink()
            except OSError:
                pass


def make_light(final: Path, light: Path, dur):
    size_mb = final.stat().st_size / 1e6
    if size_mb < 29:
        shutil.copy2(final, light)
        return
    kbps = int(min(4200, (27 * 8000 / max(1, dur)) - 128))
    run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-c:v", "libx264", "-preset", "fast", "-b:v", f"{kbps}k",
         "-maxrate", f"{int(kbps * 1.2)}k", "-bufsize", f"{kbps * 2}k", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-b:a", "128k", "-movflags", "+faststart", str(light)])


def make_thumb(video: Path, thumb: Path, dur):
    t = min(3.0, dur / 3)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
         "-vf", "scale=480:-2", "-q:v", "4", str(thumb)])


def render(proj, progress=None):
    proj = Path(proj).resolve()  # caminho relativo na linha de comando quebrava o cwd do hyperframes
    prog = progress or (lambda pct, msg: print(f"{pct:5.1f}%  {msg}", flush=True))
    prog(1, "Preparando…")
    comp = build(proj)
    edit = load_edit(proj)
    dur = num(edit.get("duration"), 10)
    mudo = proj / "render_mudo.mp4"
    hf_render(Path(comp).parent, mudo, prog, 2, 85)
    prog(87, "Juntando voz e música…")
    final = proj / "final.mp4"
    mix_audio(edit, proj, mudo, final)
    marca = marca_dagua_texto(edit, proj)
    if marca:
        prog(91, "Colocando a marca d'água do canal…")
        apply_watermark(final, marca)
    prog(93, "Criando versão leve (<30 MB)…")
    make_light(final, proj / "leve.mp4", dur)
    make_thumb(final, proj / "thumb.jpg", dur)
    try:
        mudo.unlink()
    except OSError:
        pass
    prog(100, "Pronto!")
    return final


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pj = Path(sys.argv[1])
    if "--render" in sys.argv:
        # GUARDA DE QUALIDADE: vídeo vindo de um PEDIDO.md com modelo não pode ser entregue lento, seco ou fora do estilo.
        # 1ª entrega (ainda sem final.mp4): reprovou = não renderiza. Depois da 1ª entrega só avisa (não trava edições do editor).
        if (pj / "PEDIDO.md").exists() and "--sem-checagem" not in sys.argv and not os.environ.get("ESTUDIO_SEM_CHECAGEM"):
            try:
                import checar_ritmo as _cr
                _e, _a, _i = _cr.checar(pj)
                for _l in _i:
                    print("  •", _l)
                for _l in _a:
                    print("  ⚠ AVISO:", _l)
                for _l in _e:
                    print("  ✗ ERRO:", _l)
                if _e and not (pj / "final.mp4").exists():
                    print(f"\n== REPROVADO na checagem de ritmo/fidelidade ({len(_e)} erro(s)). Corrija o edit.json (kits/saga-2d/README.md) "
                          "e rode de novo. Para ignorar de propósito: --sem-checagem ==")
                    sys.exit(2)
            except ImportError:
                pass
        print(render(pj))
    else:
        print(build(pj, hide_text="--hide-text" in sys.argv))
