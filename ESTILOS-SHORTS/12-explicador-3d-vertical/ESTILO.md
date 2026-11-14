# Estilo 12 — Explicador 3D vertical

Referências: @peraexplica · @explicandodireito.br · @garagemexplicativa · @thingsopened · @oclaud1n (Instagram, 9:16)
Vídeo de exemplo: VIDEOS-SHORTS\12-explicador-3d-vertical (relógio de corda, ~67 s)

## Visual
- Fundo escuro liso (#0d0f15), sem cenário. Um único objeto 3D estilizado (low-poly / massinha) no centro: motor, prédio, relógio…
- Câmera que gira em volta do objeto e se aproxima de cada peça explicada, sem cortes secos.
- Rótulos em PÍLULA (borda 999px) com haste apontando para a peça. Cores: branco (nome), amarelo (destaque), vermelho (alerta/negação, ex.: "0 BATERIA", "CORTADA").
- Cabeçalho pequeno no topo central: "@perfil · TEMA", Montserrat Black 34px, numa cápsula translúcida.
- Legenda GRANDE: Montserrat Black 96px, caixa alta, branca com contorno preto, 1 palavra-chave colorida (amarelo #FFD23F), até 3 palavras, a ~76% da altura.

## Ritmo / roteiro
- Gancho com o paradoxo do objeto ("não tem bateria e não para"), depois "Tudo começa aqui dentro". A câmera entra no objeto e segue a cadeia de causa e efeito, 1 peça por frase.
- Mudança de plano a cada 2-4 s. Pílula aparece na palavra falada. Fecha com um número/consequência e o CTA "Segue pra ver por dentro…".
- Voz edge-tts pt-BR (Antonio, +16%), ~170 ppm. Tempos do faster-whisper alinhados ao texto exato do roteiro.

## Como replicar (grátis/local)
- Three.js no HyperFrames, usando `_template-palco3d` (palco.py + base.html). Cada vídeo tem um `cena.js` próprio, com o objeto e as animações por evento.
- `gerar_edit.py` do vídeo 12 aplica a camada visual do estilo (cabeçalho, pílulas, legenda com destaque) por substituição. Copie a pasta, troque o roteiro, o `cena.js` e as chamadas `at()`.
- Dificuldade média-alta: cada tema pede um objeto 3D novo (~1-2 h).

## Já coberto?
Parcialmente. O estilo 03 (3D escuro por dentro) já tinha o palco escuro, o objeto em corte e os rótulos ancorados. O 12 muda a cara: pílulas com haste, legenda gigante com palavra colorida, cabeçalho @perfil · TEMA, câmera orbitando e look massinha mais saturado.
