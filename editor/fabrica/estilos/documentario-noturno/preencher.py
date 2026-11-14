# preencher.py — estilo por preset (gerado pelo Estúdio de Vídeos). O desenho está em fabrica/lib/preencher_preset.py;
# aqui só se lê o "preset" do estilo.json desta pasta. Pode editar o estilo.json à vontade.
import json
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI.parent.parent))   # pasta fabrica
from lib import preencher_preset as _PP  # noqa: E402


def preencher(ctx):
    cfg = json.loads((_AQUI / "estilo.json").read_text(encoding="utf-8-sig"))
    ed = _PP.preencher(ctx, cfg.get("preset"))
    ed["estilo"] = cfg.get("nome_curto") or cfg.get("nome", _AQUI.name).split(" (")[0]
    return ed
