# 23 — Militar com footage de combate (Military Storm)

**Dados:** Military Storm (EN) mediana 76k views, 390 views/h (melhor 1.200), 16 min ("Ukrainian sniper catches Russian motorcycles…"). Nota do usuário: militar.

## Visual
- Clipes reais de combate (drone FPV, GoPro de soldado, visão térmica verde, tanque em estrada) em tela cheia, **logo do canal fixo** no canto, cortes a cada 3-6 s, zoom em detalhe, narração dramática, música tensa; sem texto, sem legenda.

## Replicável?
**Não como está.** O footage vem de Telegram/redes de guerra (sem licença; alto risco de strike e de política de conteúdo violento/desmonetização). Versão viável:
- **Mapa top-down (06-guerra) + ícones + relógio** para narrar os mesmos eventos, com b-roll militar **licenciado** (Pexels/Pixabay têm tanques, drones, treinamento; DVIDS = domínio público do Dept. of Defense dos EUA, excelente fonte) e **clipes gerados** (LTX: visão térmica, drone sobre campo, genéricos).
- Overlays nossos: HUD de drone (mira, telemetria mono verde), filtro térmico (CSS), timestamp.

## Template no editor
- `video` b-roll DVIDS/Pexels + `html` overlay HUD (`scene: "hud-drone"` params `{alt, vel, coord}`), `scene: "termico"` (filtro verde + ruído).
- `scene: "mapa-batalha"` do 06 para o contexto.
- `text` título do evento 56px condensado.

## Dificuldade: preencher-dados (média) com a versão licenciada; **irreplicável** na versão original
Usar como "variante do 06" com HUD. Sem pessoa real identificável nos clipes gerados. Demanda alta no nicho (Yarnhub 12,6k v/h, Operations Room 1,1k) justifica a variante.
