import os
import json
card_html = '''<div class="rd">
 <div class="rd-top"><div class="rd-av">r/</div><div><div class="rd-sub">r/EuSouOBabaca</div><div class="rd-user">u/carro_do_irmao · 7 h</div></div><div class="rd-join">Participar</div></div>
 <div class="rd-title">EOB por não emprestar meu carro novo para o meu irmão?</div>
 <div class="rd-tags"><span class="rd-flair">Família</span></div>
 <div class="rd-bot"><span class="rd-pill"><svg viewBox="0 0 20 20"><path d="M10 3l7 8h-4v6H7v-6H3z" fill="#ff4500"/></svg><b>18,7 mil</b><svg viewBox="0 0 20 20"><path d="M10 17l7-8h-4V3H7v6H3z" fill="#878a8c"/></svg></span>
 <span class="rd-pill"><svg viewBox="0 0 20 20"><path d="M3 4h14v9H8l-4 3v-3H3z" fill="none" stroke="#555" stroke-width="1.8"/></svg>3,2 mil</span>
 <span class="rd-pill"><svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="6" fill="#ffd635"/><path d="M7 10l2 2 4-4" stroke="#b8860b" stroke-width="1.8" fill="none"/></svg>Prêmio</span>
 <span class="rd-pill">Compartilhar</span></div></div>'''
card_css = '''.rd{width:100%;height:100%;box-sizing:border-box;background:#fff;border-radius:26px;padding:30px 38px;font-family:'Inter',Arial,sans-serif;color:#1c1c1c;box-shadow:0 18px 60px rgba(0,0,0,.55)}
.rd-top{display:flex;align-items:center;gap:16px}.rd-av{width:62px;height:62px;border-radius:50%;background:#ff4500;color:#fff;font:900 26px 'Inter';display:flex;align-items:center;justify-content:center}
.rd-sub{font-weight:800;font-size:24px}.rd-user{font-size:19px;color:#6b6f73}.rd-join{margin-left:auto;background:#0045ac;color:#fff;font-weight:800;font-size:19px;padding:10px 22px;border-radius:30px}
.rd-title{font-weight:800;font-size:40px;line-height:1.18;margin:22px 0 14px}.rd-flair{background:#e8ecef;color:#333;font-weight:700;font-size:18px;padding:6px 14px;border-radius:20px}
.rd-bot{display:flex;gap:14px;margin-top:22px}.rd-pill{display:flex;align-items:center;gap:8px;background:#eef1f3;border-radius:30px;padding:9px 18px;font-weight:700;font-size:19px;color:#333}.rd-pill svg{width:24px;height:24px}'''
edit = {
 "version": 1, "name": "12 - Reddit Story - Estou errado por não emprestar meu carro novo ao meu irmão",
 "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000"}, "duration": 62.4, "template": "generic",
 "fonts": {"Montserrat": "fonts/Montserrat-Black.ttf", "Inter": "fonts/Inter.ttf"},
 "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
 "tracks": [{"id": "fundo", "name": "Gameplay"}, {"id": "visual", "name": "Card Reddit"}, {"id": "legenda", "name": "Legenda"}],
 "items": [
  {"id": "gp", "type": "video", "track": "fundo", "label": "Gameplay parkour", "start": 0, "dur": 62.4,
   "props": {"src": "clips/gameplay.mp4", "fill": True, "fit": "cover", "volume": 0, "motion": "none"}},
  {"id": "card", "type": "html", "track": "visual", "label": "Post do Reddit", "start": 0, "dur": 7.45, "in": "pop", "out": "fade",
   "props": {"html": card_html, "css": card_css, "x": 640, "y": 340, "w": 860, "h": 330}},
  {"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda palavra-por-palavra", "start": 7.5, "dur": 54.9,
   "props": {"words_file": "words_list.json", "per_group": 1, "x": 640, "y": 360, "size": 92, "color": "#ffffff", "dim": "#ffffff", "hl_color": "#ffd400",
             "keywords": ["mesquinho", "egoísta", "rafael", "carro", "errado", "bateu", "nunca", "não", "exagerei", "fictícia"],
             "font": "Montserrat", "weight": 900, "stroke": "#000", "stroke_w": 12, "shadow": True}},
  {"id": "fim", "type": "text", "track": "legenda", "label": "Aviso final", "start": 59.9, "dur": 2.5, "in": "fade",
   "props": {"text": "História fictícia", "x": 640, "y": 650, "size": 28, "color": "#ffffff", "font": "Inter", "weight": 700, "bg": "rgba(0,0,0,.55)", "pad": 10}}
 ],
 "build": "python os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "editor", "build_from_edit.py") . ; bash render.sh ; bash finish.sh"
}
json.dump(edit, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
