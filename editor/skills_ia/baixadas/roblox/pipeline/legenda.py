r"""legenda.py - legenda 1 palavra por vez (ASS): Montserrat ExtraBold 146 px, branca, contorno preto 13, sombra 4/7,
palavras-chave em VERMELHO #EC1C24, centro a 64% da altura (y=1229). Sem pontuacao, Title Case.
Aparece 0,03 s antes da fala e fica ate a proxima; a ultima segura 0,25 s apos o fim da voz.
(104 px do prompt original fica PEQUENO no libass -> 146 aprovado.)
Uso:  python -X utf8 pipeline\legenda.py PASTA "cidade,estátua,pedra,..."   (ou PASTA vermelhas.txt)
Saida: PASTA\legenda.ass
"""
import json, os, re, sys
import soundfile as sf

W = sys.argv[1]
arg = sys.argv[2] if len(sys.argv) > 2 else ""
if arg and os.path.exists(arg): arg = open(arg, encoding="utf8").read().replace("\n", ",")
RED = {x.strip().lower() for x in arg.split(",") if x.strip()}
SIZE, YPOS = 146, 1229
words = json.load(open(os.path.join(W, "palavras.json"), encoding="utf8"))
voz_fim = sf.info(os.path.join(W, "audio", "voz.wav")).duration

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: W,Montserrat ExtraBold,{SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H66000000,0,0,0,0,100,100,0,0,1,13,0,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
for i, w in enumerate(words):
    txt = re.sub(r"[^\wÀ-ÿ]", "", w["w"])
    key = txt.lower(); txt = txt[:1].upper() + txt[1:]
    a = w["s"] - 0.03
    b = words[i + 1]["s"] - 0.03 if i + 1 < len(words) else voz_fim + 0.25
    col = r"\c&H241CEC&" if key in RED else ""
    ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},W,,0,0,0,,{{\\an5\\pos(540,{YPOS})\\xshad4\\yshad7{col}}}{txt}")
open(os.path.join(W, "legenda.ass"), "w", encoding="utf8").write(hdr + "\n".join(ev) + "\n")
print(len(ev), "palavras;", sum(1 for w in words if re.sub(r"[^\wÀ-ÿ]", "", w["w"]).lower() in RED), "em vermelho")
