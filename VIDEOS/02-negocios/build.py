# Gera hf/index.html (estilo documentário de negócios) + edit.json
import json
DUR = 65.1
P = []   # html
T = []   # timeline js
SC = []  # cenas p/ edit.json
n = [0]
def nid(p): n[0] += 1; return f"{p}{n[0]}"

def photo(src, s, e, track, kb=(1.0, 1.1, 0, -30), fade=0.45):
    i = nid("p"); d = e - s
    P.append(f'<div id="{i}" class="clip ph" data-start="{s:.2f}" data-duration="{d:.2f}" data-track-index="{track}"><img src="media/{src}"/></div>')
    T.append(f'tl.fromTo("#{i} img",{{scale:{kb[0]},x:{kb[2]}}},{{scale:{kb[1]},x:{kb[3]},duration:{d:.2f},ease:"none"}},{s:.2f});')
    if fade: T.append(f'tl.fromTo("#{i}",{{opacity:0}},{{opacity:1,duration:{fade},ease:"power1.inOut"}},{s:.2f});')
    SC.append({"start": s, "dur": round(d, 2), "tipo": "foto_kenburns", "src": f"hf/media/{src}", "params": {"kb": kb}})
    return i

def lower(name, sub, s, e, track=8):
    i = nid("lt"); d = e - s
    P.append(f'<div id="{i}" class="clip lt" data-start="{s:.2f}" data-duration="{d:.2f}" data-track-index="{track}"><div class="ltn"><span class="bar"></span><span class="tx">{name}</span></div>' + (f'<div class="lts">{sub}</div>' if sub else '') + '</div>')
    T.append(f'tl.fromTo("#{i} .bar",{{scaleX:0}},{{scaleX:1,duration:0.45,ease:"power3.out"}},{s:.2f});')
    T.append(f'tl.fromTo("#{i} .tx",{{opacity:0,x:-24}},{{opacity:1,x:0,duration:0.45,ease:"power3.out"}},{s+0.12:.2f});')
    if sub: T.append(f'tl.fromTo("#{i} .lts",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.35}},{s+0.3:.2f});')
    T.append(f'tl.to("#{i}",{{opacity:0,duration:0.3}},{e-0.3:.2f});'); T.append(f'tl.set("#{i}",{{opacity:0}},{e-0.01:.2f});')
    SC.append({"start": s, "dur": round(d, 2), "tipo": "lower_third", "texto": name, "params": {"sub": sub}})

def date(txt, s, e, track=9):
    i = nid("dt"); d = e - s
    P.append(f'<div id="{i}" class="clip dt" data-start="{s:.2f}" data-duration="{d:.2f}" data-track-index="{track}"><div class="dtt">{txt}</div><svg width="260" height="20" viewBox="0 0 260 20"><path class="ul" d="M4 12 C 70 4, 170 18, 254 8" /></svg></div>')
    T.append(f'tl.fromTo("#{i} .dtt",{{opacity:0,y:20,scale:1.15}},{{opacity:1,y:0,scale:1,duration:0.7,ease:"power3.out"}},{s:.2f});')
    T.append(f'tl.fromTo("#{i} .ul",{{strokeDashoffset:300}},{{strokeDashoffset:0,duration:0.6,ease:"power2.out"}},{s+0.35:.2f});')
    T.append(f'tl.to("#{i}",{{opacity:0,duration:0.3}},{e-0.3:.2f});'); T.append(f'tl.set("#{i}",{{opacity:0}},{e-0.01:.2f});')
    SC.append({"start": s, "dur": round(d, 2), "tipo": "data", "texto": txt})

def title(txt, s, e, track=9, big=False):
    i = nid("tt"); d = e - s
    P.append(f'<div id="{i}" class="clip tt{" big" if big else ""}" data-start="{s:.2f}" data-duration="{d:.2f}" data-track-index="{track}"><div class="ttt">{txt}</div><svg viewBox="0 0 600 20" preserveAspectRatio="none"><path class="ul" d="M4 12 C 160 4, 420 18, 596 8"/></svg></div>')
    T.append(f'tl.fromTo("#{i} .ttt",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.6,ease:"power2.out"}},{s:.2f});')
    T.append(f'tl.fromTo("#{i} .ul",{{strokeDashoffset:700}},{{strokeDashoffset:0,duration:0.8,ease:"power2.inOut"}},{s+0.3:.2f});')
    T.append(f'tl.to("#{i}",{{opacity:0,duration:0.35}},{e-0.35:.2f});'); T.append(f'tl.set("#{i}",{{opacity:0}},{e-0.01:.2f});')
    SC.append({"start": s, "dur": round(d, 2), "tipo": "titulo", "texto": txt})

def graphic(html, s, e, anims, track=4, kind="grafico"):
    i = nid("g"); d = e - s
    P.append(f'<div id="{i}" class="clip gr" data-start="{s:.2f}" data-duration="{d:.2f}" data-track-index="{track}">{html}</div>')
    T.append(f'tl.fromTo("#{i}",{{opacity:0}},{{opacity:1,duration:0.4}},{s:.2f});')
    for a in anims: T.append(a.replace("#G", f"#{i}"))
    SC.append({"start": s, "dur": round(d, 2), "tipo": kind, "params": {"html": html[:80] + "..."}})

# ---------- roteiro visual (tempos do words.json) ----------
photo("hana.jpg", 0.0, 6.05, 0, (1.05, 1.18, 0, -40), fade=0)
title("Nintendo: das cartas aos games", 0.4, 4.4)
T.append('tl.to(".ph:first-child img",{scale:1.32,duration:0.35,ease:"power3.out"},4.45);')
photo("koppai.jpg", 5.85, 10.2, 1, (1.15, 1.02, 30, -10))
date("1889", 5.95, 10.0)
lower("Quioto, Japão", "sede original da Nintendo Koppai", 7.9, 10.05)
photo("hanaold.jpg", 10.05, 17.95, 0, (1.0, 1.12, 0, 20))
lower("Fusajiro Yamauchi", "fundador · 1889", 10.25, 14.6)
lower("Hanafuda 花札", "baralho japonês feito à mão", 14.8, 17.8)

tree = ('<div class="bgblur" style="background-image:url(media/hanaold.jpg)"></div>'
        '<div class="tree"><div class="node n1"><b>Fusajiro Yamauchi</b><i>fundador</i></div>'
        '<svg class="link" width="40" height="160" viewBox="0 0 40 160"><path d="M20 0 V160"/></svg>'
        '<div class="node n2"><b>Hiroshi Yamauchi</b><i>neto · presidente</i></div>'
        '<div class="tag">assume o comando</div></div>')
graphic(tree, 17.8, 23.1, [
    'tl.fromTo("#G .n1",{opacity:0,y:-20},{opacity:1,y:0,duration:0.5,ease:"power3.out"},18.0);',
    'tl.fromTo("#G .link path",{strokeDashoffset:160},{strokeDashoffset:0,duration:0.6},20.0);',
    'tl.fromTo("#G .n2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5,ease:"power3.out"},20.7);',
    'tl.fromTo("#G .tag",{opacity:0,scaleX:0},{opacity:1,scaleX:1,duration:0.4,ease:"power3.out"},22.2);',
    'tl.fromTo("#G .bgblur",{scale:1.1},{scale:1.2,duration:5.3,ease:"none"},17.8);'])
date("1949", 17.9, 22.9, track=9)

photo("taxi.jpg", 23.0, 27.7, 1, (1.02, 1.14, -20, 20))
date("Anos 1960", 23.1, 27.5)
cards = ('<div class="bgblur" style="background-image:url(media/taxi.jpg)"></div>'
         '<div class="cards"><div class="cd c1"><svg viewBox="0 0 64 64"><path d="M10 38 L16 24 H48 L54 38 Z M8 38 H56 V48 H8 Z"/><circle cx="18" cy="50" r="5"/><circle cx="46" cy="50" r="5"/><rect x="26" y="16" width="12" height="7"/></svg><b>Táxis</b></div>'
         '<div class="cd c2"><svg viewBox="0 0 64 64"><path d="M8 30 H56 C56 46 46 54 32 54 C18 54 8 46 8 30 Z"/><path d="M14 30 C16 20 24 16 32 16 C40 16 48 20 50 30"/></svg><b>Arroz instantâneo</b></div>'
         '<div class="strike s1"></div><div class="strike s2"></div><div class="fail">não deu certo</div></div>')
graphic(cards, 27.5, 31.0, [
    'tl.fromTo("#G .c1",{opacity:0,y:30},{opacity:1,y:0,duration:0.45,ease:"power3.out"},27.6);',
    'tl.fromTo("#G .c2",{opacity:0,y:30},{opacity:1,y:0,duration:0.45,ease:"power3.out"},28.4);',
    'tl.fromTo("#G .strike",{scaleX:0},{scaleX:1,duration:0.3,ease:"power2.out",stagger:0.12},29.95);',
    'tl.fromTo("#G .fail",{opacity:0,y:10},{opacity:1,y:0,duration:0.35},30.1);',
    'tl.to("#G .cd",{opacity:0.45,duration:0.3},30.0);'])

photo("lovetester.jpg", 30.9, 33.25, 0, (1.0, 1.08, 0, 0))
lower("Gunpei Yokoi", "engenheiro e inventor da Nintendo", 31.0, 33.1)
photo("gw0.jpg", 33.05, 36.1, 1, (1.05, 1.15, 0, -20))
lower("Game &amp; Watch", "1980 · portátil de bolso", 33.25, 36.0)
photo("gw1.jpg", 35.95, 38.35, 0, (1.12, 1.02, 0, 0))
title("Brinquedos eletrônicos", 35.2, 38.1)

photo("dk.jpg", 38.2, 45.75, 1, (1.0, 1.1, 0, 0))
date("1981", 38.3, 42.6)
lower("Donkey Kong", "arcade · Nintendo", 40.5, 43.4)
lower("Jumpman → Mario", "o herói que virou mascote", 43.5, 45.6)

photo("famicom.jpg", 45.6, 49.95, 0, (1.0, 1.1, 30, -30))
date("1983", 45.7, 49.7)
lower("Famicom", "Family Computer · Japão", 47.8, 49.8)
photo("nes.jpg", 49.8, 52.25, 1, (1.1, 1.0, -20, 20))
lower("NES", "Nintendo Entertainment System · Ocidente", 49.95, 52.1)

pts = [("1889", "Cartas"), ("1949", "Hiroshi"), ("1980", "Game &amp; Watch"), ("1981", "Donkey Kong"), ("1983", "Famicom / NES")]
tlh = '<div class="bgblur" style="background-image:url(media/hq.jpg)"></div><div class="tline"><div class="axis"></div>'
for k, (y, l) in enumerate(pts):
    tlh += f'<div class="pt pt{k}" style="left:{80 + k*260}px"><span class="dot"></span><b>{y}</b><i>{l}</i></div>'
tlh += '</div>'
graphic(tlh, 52.1, 56.85, [
    'tl.fromTo("#G .axis",{scaleX:0},{scaleX:1,duration:1.2,ease:"power2.inOut"},52.3);',
    'tl.fromTo("#G .pt",{opacity:0,y:20},{opacity:1,y:0,duration:0.4,stagger:0.45,ease:"power3.out"},52.6);',
    'tl.fromTo("#G .bgblur",{scale:1.1},{scale:1.2,duration:4.8,ease:"none"},52.1);'])

photo("hana.jpg", 56.7, 60.1, 0, (1.2, 1.05, 0, 0))
title("Tudo começou com um jogo de cartas", 56.9, 59.9, big=True)

end = ('<div class="bgblur" style="background-image:url(media/hana.jpg);filter:blur(18px) brightness(.35) grayscale(1)"></div>'
       '<div class="endc"><div class="sub">Inscreva-se</div><div class="q">Qual é o seu jogo favorito da Nintendo?</div>'
       '<svg viewBox="0 0 600 20" preserveAspectRatio="none"><path class="ul" d="M4 12 C 160 4, 420 18, 596 8"/></svg></div>')
graphic(end, 60.0, DUR, [
    'tl.fromTo("#G .sub",{opacity:0,y:20,scale:.9},{opacity:1,y:0,scale:1,duration:0.5,ease:"back.out(1.6)"},60.15);',
    'tl.fromTo("#G .q",{opacity:0,y:14},{opacity:1,y:0,duration:0.5},61.2);',
    'tl.fromTo("#G .ul",{strokeDashoffset:700},{strokeDashoffset:0,duration:0.9,ease:"power2.inOut"},61.6);'], track=6, kind="end_card")

CSS = open("style.css", encoding="utf-8").read()
html = f'''<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1280" data-height="720">
{chr(10).join(P)}
<div class="fx vig"></div><div class="fx grain"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused:true}});
{chr(10).join(T)}
tl.fromTo(".grain",{{backgroundPosition:"0px 0px"}},{{backgroundPosition:"300px 200px",duration:{DUR},ease:"steps(400)"}},0);
window.__timelines["main"] = tl;
</script></body></html>'''
open("hf/index.html", "w", encoding="utf-8").write(html)
json.dump({"canvas": {"w": 1280, "h": 720, "fps": 30}, "audio": "voz.mp3",
           "build_script": "VIDEOS/02-negocios/build.py", "composition": "hf/index.html",
           "cenas": sorted(SC, key=lambda x: x["start"])}, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(P), "clips")
