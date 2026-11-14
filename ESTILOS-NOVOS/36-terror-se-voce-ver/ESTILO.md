# Estilo 36 — Terror "Se você ver..." (protocolos de sobrevivência fictícios)

**Formato:** 16:9, 1280x720, ~1 min (escala para 8-15 min com mais regras).
**Tema:** situação cotidiana que vira ameaça ("Se o seu X fizer Y às 3 da manhã... NÃO FAÇA Z"), regras numeradas, virada final. Sempre ficção, com aviso na abertura.

## Visual
- Fundo preto com vinheta cinza leve; chão = linha branca.
- Ilustração flat: pictogramas brancos, objetos em contorno branco, vermelho (#e0182d) só no perigo (ondas, relógio, pílulas, figura "errada").
- Cartão "REGRA N" + caixa com número + linha vermelha + ordem + caixinhas 1..N.
- Ordem gigante no topo com sublinhado vermelho ("NÃO ATENDA").
- Pílulas de rótulo com borda vermelha + linha pontilhada.
- Legenda: frase em caixa alta pequena embaixo, palavras-chave em vermelho.
- Fonte: Montserrat ExtraBold/Medium (Google Fonts).

## Áudio
- Narração tensa, 2ª pessoa, frases curtas (edge-tts pt-BR-AntonioNeural, +14%, pitch -4Hz).
- Drone grave (ffmpeg) baixo com ducking; som diegético gerado (toque de celular), whoosh só na entrada de cada regra. Sem impact/pop.

## Estrutura
Aviso de ficção → gancho (situação + ordem) → detalhe estranho → Regra 1..N (cartão + cena ilustrada cada) → virada ("se você desobedecer...") → CTA ("você atenderia? comenta").

## Como reproduzir
Pasta exemplo: `<pacote>\VIDEOS-NOVOS\36-terror-se-voce-ver\`
- `roteiro.txt` → edge-tts → `whisper.py` → `montar_edit.py` (cenas `sv_protocolo` com modo/tempos) → `render.ps1`.
- Cena: `<pacote>/editor\templates\scenes\sv_protocolo.html` — modos aviso, quarto, tela, regra, contagem, mensagem, porta, cobrir, voz, fim.
