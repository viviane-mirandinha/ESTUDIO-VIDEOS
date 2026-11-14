# LORE DE QUADRINHOS

**Gênero:** canais que contam a história/origem de heróis e vilões passando a câmera por painéis de HQ (ref. Comics Explained, MerryMarvelite).
**Exemplo:** `VIDEOS-NOVOS\46-lore-de-quadrinhos` — "A origem de um herói esquecido dos anos 40" (70 s, 16:9).

## Receita
- **Tela:** 1280x720, 30 fps. Página de HQ (papel creme #f3e8cf + retícula) com 3-4 quadros de borda preta grossa (8 px).
- **Câmera:** um alvo por quadro; chega no quadro ~0,3 s antes da frase (easing in-out, leve "respiro" de zoom out no meio do caminho), deriva 4,5 % de zoom enquanto parado. Troca de página = corte seco + whoosh baixinho.
- **Texto:** só o da HQ — recordatório amarelo (Comic Neue Bold, caixa alta), balão branco, onomatopeia Bangers amarela com contorno preto e sombra deslocada. Sem legenda contínua.
- **Arte:** 100% SVG próprio (personagens, cenários, capas genéricas). Cores chapadas: azul-marinho #1d2a5c, vermelho #d8342a, amarelo #f6c21c, tinta #14110f. Ou HQ antiga de domínio público conferida (Digital Comic Museum/Wikimedia). NUNCA Marvel/DC/editoras atuais.
- **Narração:** 1ª pessoa, tom de "lore" (origem → poderes → auge → queda → fim), gancho nos 3 s, CTA de comentário com palavra-chave no fim.
- **Áudio:** edge-tts pt-BR-AntonioNeural +6 %, pad de música baixa (0,10 + ducking), whoosh só nas trocas de página.
- **Fontes:** Bangers + Comic Neue (Google Fonts, OFL).

## Reaproveitar
Copiar `template.html` + `montar_edit.py` do exemplo; cada página é uma função `PG.<nome>` com `cam` (tempos de chegada da câmera por quadro) e textos em params → tudo editável no Editor (localhost:8780).
