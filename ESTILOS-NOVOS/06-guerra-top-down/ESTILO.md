# 06 — Documentário de guerra top-down (The Operations Room · Kings and Generals · Two Sides of War)

**Dados:** The Operations Room (EN) 1,45M inscritos, mediana 406k views, 1.100 views/h; Kings and Generals 4,2M, mediana 350k, 1.700 v/h (melhor 9.300); Two Sides of War (EN, pequeno, mediana 52k, 1.000 v/h) prova que o molde funciona em canal novo. Yarnhub (3D de personagens, 12.600 v/h, mediana 7M) é o topo do nicho, mas é animação 3D de personagens — fora do alcance.

## Visual
- **Operations Room:** mapa **top-down escuro** (terreno cinza-esverdeado/azul-marinho, relevo sutil), **unidades = ícones militares** (retângulos NATO ou silhuetas de navio/avião/tanque em azul × vermelho), **setas de movimento** animadas, **relógio/hora** no canto ("07:48"), legendas de unidade em sans branca pequena com fundo preto. Cortes para **foto de arquivo P&B** do momento (5-8 s) e volta ao mapa. Zoom in/out contínuo no mapa.
- **Kings and Generals:** mapa ilustrado estilo pergaminho (mais claro), exércitos como blocos coloridos, mais texto de contexto, ilustrações de batalha pintadas.
- **Two Sides of War:** mapa simples + fotos + títulos grandes brancos.
- **Paleta:** azul-marinho/cinza do mapa, azul (#3b7dd8) × vermelho (#d23b3b) dos lados, branco das legendas, amarelo dos destaques.
- **Fontes:** sans condensada caixa alta (títulos 52-60px), mono para o relógio, sans 28px nas legendas de unidade.
- **Ritmo:** cena de mapa 8-20 s, movimentação lenta constante; corte para foto 5 s; sem legenda; música tensa de tambor; whoosh suave nas setas (sem impact).

## Mídia
GeoJSON + relevo procedural (mapa), ícones SVG de unidades (Wikimedia tem símbolos NATO em SVG), setas SVG, fotos de arquivo P&B do Wikimedia (domínio público para WW1/WW2).

## Template no editor
- `scene: "mapa-batalha"` params `{foco, hora, unidades:[{id, lado, tipo, de:[lat,lon], para:[lat,lon], t0, t1, rotulo}], setas:[...]}` — base 01-mapas em tema escuro + animação de unidades por tween entre pontos.
- `scene: "relogio"` params `{inicio, fim}` canto superior direito, mono 44px.
- `image` fotos de arquivo com Ken Burns e vinheta (igual ao 02).
- `text` título de fase ("THE FIRST WAVE") 56px condensado.

## Dificuldade: preencher-dados (média)
Mesmo mapa do 01 com camada de unidades. Ollama gera `{hora, unidade, de, para, evento}`; o problema é **precisão geográfica** (posições e horários reais) — exige fato na premissa e conferência. Vídeo de 30 min = ~80 movimentos.
