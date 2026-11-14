# Gera template.html (template_src + mapa + icones + preload) e edit.json (todos os itens editaveis no editor).
# Uso: python make.py  -> depois build_from_edit.py <pasta>
import json, math, re, os, glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
NAVY, RED, GOLD = '#1d2a5c', '#c8102e', '#f2c200'
WIPES = [9.4, 28.25, 43.97, 54.6]
DUR = 61.9
ENDS = WIPES + [DUR]
def end_of(t): return next(e for e in ENDS if e > t + 0.01)

items = []
def add(id, typ, kind, start, draw, lbl, **p):
    p.update(kind=kind, draw=draw)
    track = {'text': 'textos', 'image': 'quadro', 'html': 'quadro'}[typ]
    it = {"id": id, "type": typ, "track": track, "label": lbl, "start": round(start, 2),
          "dur": round(end_of(start) - start, 2), "by": "template", "props": p}
    if typ == 'html': p.setdefault('html', '')
    items.append(it)
def title(id, s, d, text, x, y, size=64, **k): add(id, 'text', 'title', s, d, 'Título: ' + text, text=text, x=x, y=y, size=size, **k)
def label(id, s, d, text, x, y, size=32, **k): add(id, 'text', 'label', s, d, 'Rótulo: ' + text, text=text, x=x, y=y, size=size, **k)
def pill(id, s, d, text, x, y, w=130, **k): add(id, 'text', 'pill', s, d, 'Data: ' + text, text=text, x=x, y=y, w=w, **k)
def flag(id, s, d, src, x, y, w, h, lab='', **k): add(id, 'image', 'flag', s, d, 'Bandeira ' + src, src='img/%s.svg' % src, x=x, y=y, w=w, h=h, label=lab, **k)
def icon(id, s, d, name, x, y, size=80, **k): add(id, 'image', 'icon', s, d, 'Ícone ' + name, name=name, src='img/ic/%s.svg' % name, x=x, y=y, size=size, **k)
def path(id, s, d, lab, dd, d2='', **k): add(id, 'html', 'path', s, d, lab, d=dd, d2=d2, **k)
def arrow(id, s, d, x1, y1, x2, y2, bend=0.2, **k):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2; L = math.hypot(x2 - x1, y2 - y1); nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    cx, cy = mx + nx * bend * L, my + ny * bend * L
    tx, ty = x2 - cx, y2 - cy; tl = math.hypot(tx, ty); tx, ty = tx / tl, ty / tl
    def rot(a): c, s_ = math.cos(a), math.sin(a); return (x2 - 22 * (tx * c - ty * s_), y2 - 22 * (tx * s_ + ty * c))
    h1, h2 = rot(0.5), rot(-0.5)
    path(id, s, d, 'Seta', f'M{x1:.0f},{y1:.0f} Q{cx:.0f},{cy:.0f} {x2:.0f},{y2:.0f}', f'M{h1[0]:.0f},{h1[1]:.0f} L{x2:.0f},{y2:.0f} L{h2[0]:.0f},{h2[1]:.0f}', **k)
def plus(id, s, x, y, r=18): path(id, s, 0.3, 'Sinal +', f'M{x-r},{y} H{x+r}', f'M{x},{y-r} V{y+r}', color='#222', width=6)
def xmark(id, s, d, x, y, r, **k): path(id, s, d, 'X vermelho', f'M{x-r},{y-r} L{x+r},{y+r}', f'M{x+r},{y-r} L{x-r},{y+r}', **k)

# ---------------- QUADRO 1 (0 - 9.4): o que e o Reino Unido
title('q1_t', 0.05, 0.8, 'REINO UNIDO', 640, 92, 76)
flag('q1_uk', 0.85, 0.9, 'uk', 640, 222, 230, 115)
add('q1_box', 'text', 'box', 2.0, 1.0, 'Caixa: Estado soberano', text='Estado soberano', x=640, y=345, w=380, h=74, size=40, color=NAVY)
for n, (x, s) in enumerate([(280, 3.95), (520, 4.1), (760, 4.25), (1000, 4.4)]):
    arrow(f'q1_a{n}', s, 0.4, 640 + (x - 640) * 0.25, 388, x, 452, 0.08 if x < 640 else -0.08)
label('q1_4n', 4.35, 0.6, '4 nações', 935, 345, 40, color=RED)
for id_, s, src, x, lab in [('q1_eng', 5.7, 'eng', 280, 'Inglaterra'), ('q1_sco', 6.35, 'sco', 520, 'Escócia'),
                            ('q1_wal', 7.1, 'wal', 760, 'País de Gales'), ('q1_nir', 8.3, 'nir', 1000, 'Irlanda do Norte')]:
    flag(id_, s, 0.8 if src != 'nir' else 0.85, src, x, 520, 150, 90, lab)
plus('q1_p1', 6.1, 400, 520); plus('q1_p2', 6.95, 640, 520); plus('q1_p3', 8.05, 880, 520)

# ---------------- QUADRO 2 (9.5 - 28.25): 1707 / 1536 / 1801 + mapa
add('q2_map', 'html', 'map', 9.5, 1.4, 'Mapa ilhas britânicas', regions=['sco', 'eng', 'wal', 'nir', 'irl'], tx=690, ty=45, s=1.2, sea=[900, 355, 250, 330])
for id_, s, reg, col in [('q2_feng', 11.3, 'eng', '#f19c9c'), ('q2_fsco', 12.1, 'sco', '#9dbcf0'), ('q2_fwal', 16.85, 'wal', '#9fd7a6'),
                         ('q2_firl', 23.75, 'irl', '#f6d77a'), ('q2_fnir', 23.75, 'nir', '#f6d77a')]:
    add(id_, 'html', 'fill', s, 0.6, 'Pintar ' + reg, map='q2_map', region=reg, color=col, hand=(id_ != 'q2_fnir'))
pill('q2_1707', 9.9, 0.7, '1707', 105, 105, 130)
flag('q2_eng', 11.25, 0.75, 'eng', 260, 105, 120, 72, 'Inglaterra', lsize=28)
plus('q2_p', 11.95, 362, 105, 16)
flag('q2_sco', 12.1, 0.75, 'sco', 465, 105, 120, 72, 'Escócia', lsize=28)
icon('q2_ato', 13.35, 0.7, 'scroll-text', 95, 262, 84, color='#6b4a2b')
label('q2_atol', 13.65, 0.6, 'Ato de União', 255, 262, 36)
arrow('q2_a1', 14.35, 0.5, 250, 292, 250, 345, -0.3)
title('q2_gb', 15.0, 0.8, 'GRÃ-BRETANHA', 330, 380, 56)
flag('q2_wal', 16.45, 0.8, 'wal', 260, 500, 120, 72, 'País de Gales', lsize=28)
arrow('q2_aw', 17.9, 0.6, 1045, 455, 935, 518, 0.25)
label('q2_anx', 18.1, 0.6, 'anexado!', 420, 470, 34, color=RED)
pill('q2_1536', 19.45, 0.7, '1536', 105, 500, 130)
icon('q2_vote', 21.3, 0.55, 'vote', 560, 500, 76)
xmark('q2_vx', 21.85, 0.45, 560, 500, 34, width=8)
label('q2_vl', 22.4, 0.6, 'sem voto', 560, 562, 30, color=RED)
flag('q2_stp', 23.7, 0.8, 'stp', 260, 628, 110, 66, 'Irlanda', lsize=28)
pill('q2_1801', 24.6, 0.7, '1801', 105, 628, 130)
icon('q2_sw', 25.85, 0.6, 'swords', 430, 628, 72)
label('q2_reb', 26.5, 0.7, 'rebelião', 560, 612, 32, color=RED)
xmark('q2_sx', 27.5, 0.45, 430, 628, 30, width=8)

# ---------------- QUADRO 3 (28.3 - 43.97): 1922 + 4/4/4/1
add('q3_map', 'html', 'map', 28.3, 1.2, 'Mapa ilha da Irlanda', regions=['irl', 'nir'], tx=30, ty=-680, s=3.0, sea=[275, 370, 250, 300])
pill('q3_1922', 28.85, 0.7, '1922', 590, 110, 130)
add('q3_firl', 'html', 'fill', 30.6, 0.7, 'Pintar sul (Irlanda)', map='q3_map', region='irl', color='#8fd19a')
flag('q3_irl', 31.4, 0.9, 'irl', 255, 470, 120, 80, 'Independência', lsize=30)
add('q3_fnir', 'html', 'fill', 33.35, 0.6, 'Pintar norte', map='q3_map', region='nir', color='#f19c9c')
flag('q3_nir', 33.6, 0.9, 'nir', 600, 235, 130, 65, 'Irlanda do Norte', lsize=28)
arrow('q3_an', 34.5, 0.4, 425, 210, 525, 230, -0.2)
label('q3_prot', 34.6, 0.6, 'protestante', 600, 330, 32, color=NAVY)
label('q3_fic', 35.35, 0.5, 'ficou!', 600, 375, 38, color=RED)
for r, (y, s, num, ic, txt, col) in enumerate([(140, 37.0, '4', 'ball', 'times de futebol', None), (250, 38.95, '4', 'scale', 'sistemas de lei', None),
                                                  (360, 40.65, '4', 'map-pin', 'capitais', None), (490, 42.2, '1', 'globe', 'assento na ONU', RED)]):
    title(f'q3_n{r}', s, 0.35, num, 785, y, 70, **({'color': '#f08080'} if col else {}))
    icon(f'q3_i{r}', s + 0.3, 0.45, ic, 870, y, 70, **({'fill': '#222'} if ic == 'ball' else {}))
    label(f'q3_l{r}', s + 0.6, 0.55, txt, 920, y, 36, anchor='start', **({'color': col} if col else {}))
label('q3_caps', 41.45, 0.75, 'Londres · Edimburgo · Cardiff · Belfast', 990, 410, 28, color='#555')

# ---------------- QUADRO 4 (44 - 54.6): o nome oficial
icon('q4_cr', 44.35, 0.6, 'crown', 215, 115, 100, fill=GOLD)
label('q4_el', 44.75, 0.6, 'Rainha Elizabeth II', 225, 200, 36)
label('q4_sig', 45.0, 0.9, 'Elizabeth R', 560, 130, 72, font='Caveat', color=NAVY)
add('q4_box', 'text', 'box', 46.1, 3.7, 'Caixa: nome oficial', text='Rainha do Reino Unido da Grã-Bretanha\ne Irlanda do Norte', x=615, y=330, w=990, h=150, size=44)
add('q4_u1', 'html', 'uline', 50.6, 0.5, 'Sublinhar Grã-Bretanha', ref='q4_box', word='Grã-Bretanha', color=RED)
add('q4_u2', 'html', 'uline', 51.1, 0.5, 'Sublinhar Irlanda do Norte', ref='q4_box', word='Irlanda do Norte', color=RED)
flag('q4_uk', 52.5, 0.6, 'uk', 300, 515, 180, 90)
title('q4_1e', 52.85, 0.55, '1 ESTADO', 300, 622, 56)
arrow('q4_a', 53.35, 0.3, 410, 520, 570, 520, 0.0)
for n, (src, x, y) in enumerate([('eng', 645, 482), ('sco', 770, 482), ('wal', 645, 562), ('nir', 770, 562)]):
    flag(f'q4_f{n}', 53.45 + n * 0.14, 0.32, src, x, y, 100, 60, hand=(n == 3))
title('q4_4p', 53.95, 0.5, '4 PAÍSES', 708, 645, 56, color='#f08080')

# ---------------- QUADRO 5 (54.65 - fim): erro comum + inscreva-se
flag('q5_eng', 55.2, 1.0, 'eng', 520, 245, 300, 180)
label('q5_tudo', 55.95, 0.7, 'tudo Inglaterra?', 520, 385, 44, color=NAVY)
xmark('q5_x', 57.05, 0.5, 520, 245, 110, width=14)
label('q5_erro', 57.55, 0.6, 'erro comum!', 520, 445, 44, color=RED)
pill('q5_sub', 58.45, 0.7, 'INSCREVA-SE', 470, 580, 330, h=76, size=46, bg=RED)
icon('q5_bell', 58.95, 0.45, 'bell', 690, 580, 70, fill=GOLD)
icon('q5_globe', 59.4, 0.5, 'globe', 830, 580, 76, color='#1f6fb2')
label('q5_mapas', 59.7, 0.6, '+ mapas', 960, 580, 40, color=NAVY)

# ---------------- parametros
params = [
    {"id": "camera", "type": "param", "label": "Câmera [t, x, y, zoom]", "props": {"value": [
        [0, 640, 200, 1.12], [1.9, 640, 300, 1.06], [3.9, 640, 400, 1.0], [5.6, 400, 470, 1.1], [7.0, 860, 470, 1.1], [8.4, 640, 380, 1.0],
        [9.5, 640, 360, 1.0], [11.2, 400, 200, 1.12], [13.3, 400, 300, 1.12], [16.4, 640, 420, 1.06], [17.8, 900, 480, 1.15], [19.4, 400, 480, 1.12],
        [23.6, 582, 520, 1.1], [26.0, 400, 600, 1.12],
        [28.3, 640, 360, 1.0], [30.5, 330, 360, 1.1], [33.3, 450, 260, 1.12], [36.9, 900, 250, 1.1], [40.6, 900, 400, 1.1], [43.0, 640, 360, 1.0],
        [44.0, 640, 360, 1.0], [44.3, 350, 180, 1.12], [46.0, 640, 330, 1.06], [50.4, 640, 330, 1.12], [52.4, 500, 520, 1.1], [54.2, 640, 360, 1.0],
        [54.6, 640, 360, 1.0], [55.2, 520, 300, 1.1], [58.3, 640, 450, 1.06], [60.5, 640, 360, 1.0]]}},
    {"id": "wipes", "type": "param", "label": "Limpar quadro (segundos)", "props": {"value": WIPES}},
    {"id": "boneco", "type": "param", "label": "Boneco [t, pose, balão]  poses: neutro duvida pensando aponta feliz bravo surpreso vergonha joinha", "props": {"value": [
        [0, 'neutro', ''], [0.8, 'duvida', 'Não é um país?!'], [3.0, 'neutro', ''], [5.6, 'aponta', ''], [9.5, 'neutro', ''], [15.0, 'feliz', ''],
        [17.9, 'pensando', ''], [21.3, 'bravo', 'Sem voto?!'], [23.6, 'neutro', ''], [25.9, 'surpreso', ''], [28.3, 'neutro', ''], [31.4, 'feliz', ''],
        [33.4, 'pensando', ''], [36.0, 'aponta', ''], [42.2, 'surpreso', ''], [44.0, 'neutro', ''], [50.2, 'pensando', ''], [52.5, 'feliz', 'Ahh, entendi!'],
        [54.6, 'pensando', ''], [57.0, 'vergonha', ''], [58.4, 'joinha', '']]}},
]
edit = {"version": 1, "name": "01 - WHITEBOARD QUADRO - Por que o Reino Unido tem quatro países dentro de um só",
        "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#ffffff"}, "duration": DUR, "template": "local",
        "fonts": {"Kalam": "fonts/Kalam-Bold.ttf", "Lilita One": "fonts/LilitaOne-Regular.ttf", "Caveat": "fonts/Caveat.ttf", "Patrick Hand": "fonts/PatrickHand-Regular.ttf"},
        "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "quadro", "name": "Desenhos (bandeiras, mapa, setas)"}, {"id": "textos", "name": "Textos / datas"}],
        "items": params + items}
json.dump(edit, open('edit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------- template.html
M = json.load(open('map_paths.json'))
ICONS = {}
for f in glob.glob('img/ic/*.svg'):
    s = open(f, encoding='utf-8').read()
    ICONS[os.path.basename(f)[:-4]] = re.sub(r'\s+', ' ', re.search(r'<svg[^>]*>(.*)</svg>', s, re.S).group(1)).strip()
ICONS['ball'] = ('<circle cx="12" cy="12" r="10"/><path data-f="" d="M12 7.5l4.3 3.1-1.6 5h-5.4l-1.6-5z"/>'
                 '<path d="M12 7.5V2M16.3 10.6l4.9-1.7M14.7 15.6l3 4.1M9.3 15.6l-3 4.1M7.7 10.6l-4.9-1.7"/>')
pre = ''.join(f'<img src="{f.replace(os.sep, "/")}">' for f in sorted(glob.glob('img/*.svg')))
t = open('template_src.html', encoding='utf-8').read()
t = t.replace('__MAPDATA__', json.dumps(M)).replace('__ICONS__', json.dumps(ICONS)).replace('__PRELOAD__', pre)
open('template.html', 'w', encoding='utf-8').write(t)
print('itens', len(items), 'template', len(t))
