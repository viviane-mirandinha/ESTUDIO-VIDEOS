# vs_instalar.py — baixa e instala o VoiceStudio (app de clonagem de voz/dublagem, AGPL-3.0) pelo painel, em Ajustes.
# Só usa o instalador OFICIAL do GitHub (debpalash/VoiceStudio) e confere o SHA-256 publicado no mesmo release.
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = "debpalash/VoiceStudio"
PASTA = Path(__file__).resolve().parents[2] / "voicestudio-instalacao"   # editor/voicestudio-instalacao
LOG = PASTA / "instalacao.log"
_UA = {"User-Agent": "estudio-videos-painel"}
_cache = {"t": 0.0, "rel": None}


def log(msg):
    try:
        PASTA.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg).rstrip() + "\n")
    except Exception:
        pass


def log_final(n=60):
    try:
        return "\n".join(LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-n:])
    except Exception:
        return ""


def _http(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=timeout)


def _arch():
    return "arm64" if "ARM" in platform.machine().upper() else "x64"


def release():
    """Última versão publicada para Windows: {tag, nome, url, tamanho, sha_url}. Guarda 10 min."""
    if _cache["rel"] and time.time() - _cache["t"] < 600:
        return _cache["rel"]
    with _http(f"https://api.github.com/repos/{REPO}/releases/latest") as r:
        d = json.load(r)
    alvo = f"-win-{_arch()}.exe"
    a = next((x for x in d.get("assets", []) if x["name"].endswith(alvo)), None)
    if not a:
        raise RuntimeError(f"O release {d.get('tag_name')} não tem instalador para Windows {_arch()}.")
    sha = next((x for x in d["assets"] if x["name"] == "SHA256SUMS.txt"), None)
    rel = {"tag": d.get("tag_name"), "nome": a["name"], "url": a["browser_download_url"], "tamanho": a["size"],
           "sha_url": sha["browser_download_url"] if sha else None}
    _cache.update(t=time.time(), rel=rel)
    return rel


def achar_instalado():
    """Procura o app instalado (registro do Windows + pastas comuns). Devolve {exe, versao} ou None."""
    if sys.platform != "win32":
        return None
    try:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for sub in (r"Software\Microsoft\Windows\CurrentVersion\Uninstall", r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"):
                try:
                    k = winreg.OpenKey(hive, sub)
                except OSError:
                    continue
                for i in range(winreg.QueryInfoKey(k)[0]):
                    try:
                        s = winreg.OpenKey(k, winreg.EnumKey(k, i))
                        nome = str(winreg.QueryValueEx(s, "DisplayName")[0])
                    except OSError:
                        continue
                    if not re.search(r"voice\s*studio|omnivoice", nome, re.I):
                        continue
                    vers = ""
                    try:
                        vers = str(winreg.QueryValueEx(s, "DisplayVersion")[0])
                    except OSError:
                        pass
                    for campo in ("DisplayIcon", "InstallLocation"):
                        try:
                            v = str(winreg.QueryValueEx(s, campo)[0]).strip('"').split(",")[0]
                        except OSError:
                            continue
                        p = Path(v)
                        if p.is_dir():
                            p = next((c for c in p.glob("*.exe") if not c.name.lower().startswith(("unins", "uninstall"))), p)
                        if p.is_file() and p.suffix.lower() == ".exe":
                            return {"exe": str(p), "versao": vers}
    except Exception:
        pass
    bases = [os.environ.get("LOCALAPPDATA", "") + r"\Programs", os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")]
    for b in bases:
        if not b:
            continue
        for d in Path(b).glob("*"):
            if d.is_dir() and re.search(r"voice\s*studio|omnivoice", d.name, re.I):
                e = next((c for c in d.glob("*.exe") if not c.name.lower().startswith(("unins", "uninstall"))), None)
                if e:
                    return {"exe": str(e), "versao": ""}
    return None


def status():
    inst = achar_instalado()
    out = {"windows": sys.platform == "win32", "instalado": bool(inst), "exe": (inst or {}).get("exe"), "versao": (inst or {}).get("versao"),
           "dados": (Path(os.environ.get("APPDATA", "")) / "OmniVoice").is_dir(), "log": log_final(40)}
    try:
        r = release()
        out["ultima"] = {"tag": r["tag"], "mb": round(r["tamanho"] / 1e6)}
    except Exception as e:
        out["ultima"] = None
        out["erro_rede"] = str(e)[:150]
    return out


def abrir():
    i = achar_instalado()
    if not i:
        raise RuntimeError("O VoiceStudio não está instalado.")
    subprocess.Popen([i["exe"]], cwd=str(Path(i["exe"]).parent))
    return i


def _sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _baixar(url, dest, total, prog, lo, hi, nome):
    log(f"Baixando {url}")
    t0 = time.time()
    with _http(url, 30) as r, open(dest, "wb") as f:
        feito = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            feito += len(b)
            seg = max(time.time() - t0, 0.1)
            falta = (total - feito) / (feito / seg) if feito and total else 0
            prog(lo + (hi - lo) * min(feito / max(total, 1), 1),
                 f"Baixando {nome}: {feito/1e6:.0f} de {total/1e6:.0f} MB" + (f" (faltam uns {int(falta // 60)} min {int(falta % 60)} s)" if falta > 5 else ""))
    if total and dest.stat().st_size != total:
        raise RuntimeError(f"Download incompleto ({dest.stat().st_size} de {total} bytes). Verifique a internet e tente de novo.")


def instalar(prog):
    """Baixa o instalador oficial, confere o SHA-256 e abre. Retorna {versao, exe}. Erros viram RuntimeError com texto simples."""
    if sys.platform != "win32":
        raise RuntimeError("Este botão instala só no Windows. No Mac/Linux use as instruções em voicestudio.sh.")
    PASTA.mkdir(parents=True, exist_ok=True)
    log("=== Nova tentativa de instalação ===")
    if (i := achar_instalado()):
        log(f"Já instalado: {i}")
        return {"versao": i.get("versao"), "exe": i["exe"], "ja_tinha": True}
    prog(2, "Procurando a última versão no GitHub…")
    try:
        rel = release()
    except Exception as e:
        log(f"Falha ao consultar o GitHub: {e}")
        raise RuntimeError(f"Não consegui falar com o GitHub (github.com). Veja a internet/antivírus. Detalhe: {str(e)[:200]}")
    livre = shutil.disk_usage(PASTA).free / 1e9
    log(f"Versão {rel['tag']} · instalador {rel['tamanho']/1e6:.0f} MB · disco livre {livre:.1f} GB")
    if livre < 8:
        raise RuntimeError(f"Pouco espaço no disco ({livre:.1f} GB livres). O VoiceStudio precisa de uns 8-10 GB com os modelos de voz. Libere espaço e tente de novo.")
    dest = PASTA / rel["nome"]
    _baixar(rel["url"], dest, rel["tamanho"], prog, 4, 68, rel["nome"])
    prog(70, "Conferindo se o arquivo é o original (SHA-256)…")
    if rel["sha_url"]:
        with _http(rel["sha_url"]) as r:
            txt = r.read().decode("utf-8", "replace")
        m = re.search(r"([0-9a-fA-F]{64})\s+\*?" + re.escape(rel["nome"]), txt)
        real = _sha256(dest)
        if m and m.group(1).lower() != real:
            dest.unlink(missing_ok=True)
            log(f"SHA-256 NÃO bate: esperado {m.group(1)} · baixado {real}")
            raise RuntimeError("O arquivo baixado não bate com o SHA-256 oficial (veio corrompido). Apaguei e não instalei. Tente de novo.")
        log("SHA-256 confere" if m else "SHA-256 do arquivo não estava na lista; segui sem conferir")
    prog(74, "Abrindo o instalador… (se o Windows perguntar “Permitir alterações?”, clique em Sim)")
    log(f"Executando {dest}")
    try:
        p = subprocess.Popen([str(dest)], cwd=str(PASTA))
    except OSError as e:
        if getattr(e, "winerror", 0) != 740:
            raise RuntimeError(f"O Windows não deixou abrir o instalador: {e}")
        log("Precisa de administrador: abrindo com Start-Process -Verb RunAs")
        p = subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process -FilePath '{dest}' -Verb RunAs -Wait"],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    t0 = time.time()
    try:
        while p.poll() is None:
            if time.time() - t0 > 30 * 60:
                raise RuntimeError("O instalador passou de 30 minutos sem terminar. Veja se há uma janela dele esperando você.")
            prog(min(74 + (time.time() - t0) / 60, 94), "Instalando… acompanhe a janela do instalador (clique nos botões dela se pedir).")
            time.sleep(2)
    except BaseException:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
        raise
    log(f"Instalador terminou com código {p.returncode}")
    time.sleep(3)
    i = achar_instalado()
    if not i:
        raise RuntimeError(f"O instalador fechou (código {p.returncode}) mas não achei o VoiceStudio instalado. Pode ter sido cancelado ou bloqueado pelo antivírus.")
    log(f"Instalado: {i}")
    return {"versao": i.get("versao") or rel["tag"], "exe": i["exe"]}


def prompt_ajuda(extra=""):
    return (
        "Você é o assistente de instalação do painel Estúdio de Vídeos. A pessoa quer instalar o **VoiceStudio** (app de clonagem de voz/dublagem, "
        "repositório oficial github.com/debpalash/VoiceStudio, site voicestudio.sh) neste PC Windows e a instalação pelo botão do painel falhou ou "
        "precisa de acompanhamento. Fale em português simples (a pessoa não é programadora).\n\n"
        f"Pasta de trabalho (cwd): {PASTA}\n"
        f"Log da instalação do painel: {LOG}  (leia o final dele primeiro)\n"
        "Instalador baixado (se existir) fica nesta mesma pasta (VoiceStudio-*-win-*.exe).\n\n"
        "## O que fazer\n"
        "1. Leia o log e descubra a causa (internet, disco cheio, SHA-256 que não bate, antivírus/SmartScreen, falta de administrador, instalador cancelado, etc.). "
        "Confira também o PC (espaço livre, RAM, GPU) só com comandos de leitura.\n"
        "2. Se der para corrigir sozinho, corrija e instale: baixe de novo o `.exe` OFICIAL do release do GitHub (api.github.com/repos/debpalash/VoiceStudio/releases/latest), "
        "confira o SHA-256 com o `SHA256SUMS.txt` do mesmo release e execute o instalador. Se precisar de um clique da pessoa (Permitir alterações, SmartScreen "
        "“Mais informações → Executar assim mesmo”), diga exatamente qual.\n"
        "3. Depois confirme se instalou (registro do Windows em Uninstall, ou pasta em %LOCALAPPDATA%\\Programs).\n"
        "4. Termine com um resumo curto: o que deu errado, o que você fez, se ficou instalado, e o que a pessoa deve fazer agora (se algo).\n\n"
        "## Regras (obrigatórias)\n"
        "- Só use a fonte oficial acima. Nada de instaladores de outros sites, nem `irm ... | iex` de endereços que você não verificou.\n"
        "- Não apague nem mude nada fora da pasta de trabalho e da pasta do próprio VoiceStudio. Não mexa em `VIDEOS/`, `.venv/`, `.env` nem nos arquivos do painel.\n"
        "- Não mude configurações de segurança do Windows (antivírus, SmartScreen, políticas), não desative nada. Se o antivírus bloqueou, explique e deixe a pessoa decidir.\n"
        "- Não digite nem peça senhas/chaves. Não instale outros programas grandes sem explicar na resposta.\n"
        "- Lembre à pessoa, se for relevante: este PC pode não ter placa NVIDIA (o VoiceStudio roda na CPU, mais devagar) e o modelo padrão (OmniVoice) tem licença "
        "CC-BY-NC (não comercial); clonar voz só com autorização de quem é a voz.\n"
        + (f"\n## O que a pessoa escreveu\n{extra.strip()[:1500]}\n" if (extra or "").strip() else "")
    )
