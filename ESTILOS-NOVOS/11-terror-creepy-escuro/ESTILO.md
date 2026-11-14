# 11 — Histórias de terror / mistérios da internet, escuro (Mr. Nightmare · Chilling Scares · Marcos Campos)

**Dados:** Mr. Nightmare (EN) mediana 978k views, 2.080 views/h (melhor 10.400); Chilling Scares (EN) mediana 2,1M, 4.300 v/h ("Obscure Internet Mysteries"); Marcos Campos (PT) mediana 246k, 930 v/h (melhor 6.100). Nexpo (mediana 2,7M) e Lemmino (8,4M) são o topo do nicho com produção pesada.

## Visual
- **Mr. Nightmare:** imagem escura quase estática (floresta à noite, corredor, casa) com **zoom lentíssimo** e **ruído/grão**; título do caso em **sans/condensada vermelha ou branca** sobre preto no início de cada história ("Story 1: The Cabin"); às vezes print de post/Reddit do relato. 90 % da tela é preto/azul-escuro; raios de lanterna, névoa. Sem legenda.
- **Chilling Scares:** prints de sites antigos/fóruns, vídeos pixelados em moldura, texto mono verde/branco "terminal", glitch, timestamps; cada "mistério" abre com card numerado.
- **Marcos Campos (PT):** imagens geradas/arquivo em tela cheia escurecida, título grande vermelho, vinheta fechada, música de tensão.
- **Paleta:** preto, azul-noite (#0b1020), vermelho (#c1121f), verde-terminal (#39ff14) nos prints. Vinheta forte.
- **Ritmo:** planos longos (8-15 s) com zoom; corte suave; música ambiente + drones graves; narração lenta e baixa; **nada de jump scare / SFX de impacto** (combina com a regra do usuário).

## Mídia
Imagens geradas localmente (Flux/LTX: floresta, cabana, corredor, estrada à noite — sem rosto), fotos escuras Pexels/Pixabay, prints de "fórum" **gerados em HTML** (fake-layout genérico, sem logo real), overlay VHS/glitch em CSS/SVG. Zero material com direitos.

## Template no editor
- `image` tela cheia `motion: zoom_in 0.06` + `html` overlay (vinheta + grão + leve flicker).
- `scene: "titulo-historia"` params `{numero, titulo}` — fundo preto, "HISTÓRIA 1" em condensada vermelha 64px + título branco 48px, fade lento.
- `scene: "print-forum"` params `{usuario, data, texto}` — layout de post genérico (escuro) com scroll lento e cursor.
- `scene: "terminal"` params `{linhas:[...]}` — texto mono verde digitando.
- `scene: "mapa-ponto"` (do 02) para local do caso.
- Áudio: drone grave `volume 0.08`, sem SFX.

## Dificuldade: preencher-dados (fácil)
É o mais simples dos escuros: poucas cenas, imagens genéricas reutilizáveis (banco de 50 imagens noturnas cobre dezenas de vídeos — atenção à diversidade/cooldown). Roteiro Ollama de relatos em 1ª pessoa funciona bem (histórias fictícias "baseadas em relato" — sem pessoa real). Gap em PT confirmado (Marcos Campos é o único médio).
