"""Embute os widgets animados (kits/saga-2d/widgets.js) no template.html de um vídeo do estilo "Saga sobrevivência 2D".
Pode rodar quantas vezes quiser (troca o bloco antigo pelo atual).

  python kits/saga-2d/embutir.py <pasta_do_video>        # usa <pasta>/template.html
"""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
INI, FIM = "/*WIDGETS-BEGIN*/", "/*WIDGETS-END*/"
ANCORA = "/* ---------------- montagem ---------------- */"


def embutir(pasta):
    t = Path(pasta) / "template.html"
    if not t.exists():
        raise SystemExit(f"[embutir] não achei {t} (copie o template.html do modelo antes)")
    html = t.read_text(encoding="utf-8")
    html = re.sub(re.escape(INI) + r".*?" + re.escape(FIM) + r"\n?", "", html, flags=re.S)
    if ANCORA not in html:
        raise SystemExit("[embutir] o template não tem o marcador '/* ---------------- montagem ---------------- */' — use o template do modelo 01-saga-sobrevivencia-2d")
    bloco = f"{INI}\n{(KIT / 'widgets.js').read_text(encoding='utf-8')}\n{FIM}\n"
    html = html.replace(ANCORA, bloco + ANCORA, 1)
    t.write_text(html, encoding="utf-8")
    print(f"[embutir] widgets embutidos em {t}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    embutir(sys.argv[1])
