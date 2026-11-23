# preparar.py — do pedido até o plano de cenas: roteiro -> voz -> tempo das palavras -> plano.json. Zero token.
#   python kits/blender-3d/preparar.py <pasta-do-video>
# Lê <pasta>/pedido.json: {tema, roteiro, voz ("motor:nome"), modelo_ollama, idioma, duracao, predefinicao, cenario}.
# Fala com a fila do painel por linhas "@@pct|mensagem".
import json, re, shutil, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent.parent
sys.path.insert(0, str(RAIZ / "editor" / "fabrica"))
sys.path.insert(0, str(KIT))


def prog(p, msg):
    print(f"@@{p}|{msg}", flush=True)


def achar_voz(pasta: Path):
    for n in ("voz.mp3", "voz.wav", "voz.m4a"):
        if (pasta / n).exists():
            return pasta / n
    return None


def grafia_do_roteiro(words, roteiro):
    """Alinha as palavras do Whisper com o roteiro que a voz leu: onde o Whisper errou a grafia ("carro lá" -> "Carla"),
    usa as palavras do roteiro mantendo o tempo do áudio (quando muda a quantidade de palavras, divide o mesmo trecho de
    tempo entre elas). Só mexe em trechos de até 3 palavras e parecidos; nunca inventa fala nem tempo."""
    import difflib
    norm = lambda t: re.sub(r"[^\w]", "", t.lower())
    R = roteiro.split()
    a, b = [norm(w.get("w", "")) for w in words], [norm(x) for x in R]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        trecho, novas = words[i1:i2], R[j1:j2]
        if op == "equal":
            out += [{**w, "w": R[j1 + k]} for k, w in enumerate(trecho)]   # pega a pontuação e a maiúscula do roteiro
        elif op == "replace" and 0 < len(trecho) <= 3 and 0 < len(novas) <= 3 and difflib.SequenceMatcher(None, "".join(a[i1:i2]), "".join(b[j1:j2])).ratio() >= 0.5:
            if len(trecho) == len(novas):
                out += [{**w, "w": novas[k]} for k, w in enumerate(trecho)]
            else:
                s0, e0 = trecho[0]["s"], trecho[-1]["e"]
                pesos = [max(1, len(x)) for x in novas]
                t = s0
                for x, pz in zip(novas, pesos):
                    dt = (e0 - s0) * pz / sum(pesos)
                    out.append({"w": x, "s": round(t, 3), "e": round(t + dt, 3)})
                    t += dt
        elif op in ("replace", "delete"):
            out += trecho   # fala diferente do roteiro: mantém o que o Whisper ouviu
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pasta = Path(sys.argv[1]).resolve()
    ped = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    from lib import ollama, tts
    from lib.transcrever import transcrever
    import planejar

    # 1) roteiro
    rot = (ped.get("roteiro") or "").strip()
    if not rot and (pasta / "roteiro.txt").exists():
        rot = (pasta / "roteiro.txt").read_text(encoding="utf-8").strip()
    if not rot:
        if not ped.get("tema"):
            sys.exit("O pedido não tem tema nem roteiro.")
        prog(3, "Escrevendo o roteiro com a IA local (1-2 min)…")
        palavras = int(float(ped.get("duracao") or 45) * 2.5)
        r = ollama.roteiro(ped["tema"], palavras, ped.get("canal", ""), "narrador simpático de um vídeo animado em 3D", modelo=ped.get("modelo_ollama") or "qwen2.5:7b")
        rot = r["roteiro"]
    (pasta / "roteiro.txt").write_text(rot, encoding="utf-8")
    prog(15, "Roteiro pronto.")

    # 2) voz (usa a voz que já estiver na pasta, ex.: narração própria)
    voz = achar_voz(pasta)
    if voz:
        prog(40, f"Usando a voz que já está na pasta ({voz.name}).")
    else:
        prog(18, "Gravando a narração (voz)…")
        motor, _, nome = (ped.get("voz") or "edge:pt-BR-ThalitaMultilingualNeural").partition(":")
        try:
            voz, usado = tts.falar(rot, pasta, motor or "auto", nome or None)
        except Exception as e:
            # voz pedida indisponível (ex.: Fish sem crédito): usa a voz grátis, mas AVISA (CLAUDE.md: não esconder)
            aviso = f"A voz pedida ({ped.get('voz') or 'padrão'}) não funcionou: {str(e).splitlines()[-1][:160]}. Usei a voz grátis (edge). Para trocar, escolha outra voz em Ajustes e refaça a voz."
            prog(30, "Voz pedida indisponível: usando a voz grátis…")
            with open(pasta / "DECISOES.md", "a", encoding="utf-8") as f:
                f.write(f"- {aviso}\n")
            voz, usado = tts.falar(rot, pasta, "edge", "pt-BR-ThalitaMultilingualNeural")
        prog(40, "Voz pronta.")

    # 3) tempo de cada palavra
    prog(42, "Descobrindo o tempo de cada palavra (Whisper)…")
    idioma = (ped.get("idioma") or "pt-BR").split("-")[0]
    transcrever(voz, pasta / "words.json", idioma=idioma)
    wj = pasta / "words.json"
    wj.write_text(json.dumps(grafia_do_roteiro(json.loads(wj.read_text(encoding="utf-8")), rot), ensure_ascii=False), encoding="utf-8")
    prog(65, "Tempos prontos.")

    # 4) plano de cenas
    prog(68, "Planejando as cenas…")
    planejar.planejar(pasta, usar_ia=bool(ped.get("usar_ia", True)), refazer=True)
    por = ped.get("ambiente", "ollama")      # quem projeta o ambiente do vídeo: "ollama" (grátis), "claude" ou "nenhum" (sala pronta antiga)
    (pasta / "ambiente.json").unlink(missing_ok=True)
    if por != "nenhum":
        prog(80, "Claude projetando o ambiente do vídeo…" if por == "claude" else "Projetando o ambiente do vídeo (IA local)…")
        try:
            import ambiente
            ambiente.projetar(pasta, usar_ia=bool(ped.get("usar_ia", True)), por=por)
        except Exception as e:   # noqa: BLE001  (o vídeo segue com a sala pronta)
            print(f"(Não consegui projetar o ambiente: {str(e)[:120]} — usei a sala pronta.)", flush=True)
    if ped.get("buscar_modelos", True):
        prog(85, "Procurando modelos 3D livres (CC0) para o tema…")
        try:
            import buscar_modelos
            buscar_modelos.aplicar(pasta, usar_ia=bool(ped.get("usar_ia", True)))
        except Exception as e:   # sem internet ou site fora: o vídeo segue sem os modelos
            print(f"(Não consegui buscar modelos 3D: {str(e)[:120]} — o vídeo segue sem eles.)", flush=True)
    prog(100, "Plano de cenas pronto.")


if __name__ == "__main__":
    main()
