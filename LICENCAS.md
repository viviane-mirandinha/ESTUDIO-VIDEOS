# Licenças e origem do que está no pacote

Tudo que está aqui foi feito pelo autor do pacote ou é de uso livre. Nenhum programa pago ou licenciado vai junto.

| Item | Origem | Licença |
|---|---|---|
| `editor/` (painel), `editor/fabrica/`, templates e scripts de `VIDEOS*/`, `kits/` | Código próprio | Uso livre entre amigos |
| `VIDEOAULAS/` | Gravadas pelo autor do pacote | Uso pessoal de quem recebeu o pacote |
| HyperFrames 0.7.111 (renderizador) | npm `hyperframes` (HeyGen) — instalado pelo setup, não vem no zip | Apache-2.0 |
| Chrome headless | baixado por `hyperframes browser ensure` | Licença do Chrome for Testing |
| GSAP (animação, via CDN) | GreenSock / Webflow | Licença padrão gratuita do GSAP (uso comercial liberado) |
| Three.js (3D, via CDN) | three.js | MIT |
| Fontes (`recursos/fontes/` e pastas `fonts/`) | Baixadas direto do Google Fonts | SIL Open Font License 1.1 (`recursos/fontes/licencas/`) |
| Mapa-múndi `recursos/mapas/countries50m.geojson` | Natural Earth 1:50m | Domínio público |
| `recursos/sfx/whoosh.wav` | Gerado com ffmpeg | Próprio |
| Fotos em `*/img/` | Wikimedia Commons, Library of Congress, Pixabay | Domínio público, CC ou licença Pixabay — créditos em `img/creditos.json` quando houver. Confira antes de publicar. |
| faster-whisper / modelos Whisper | SYSTRAN / OpenAI | MIT |
| edge-tts | biblioteca que usa o serviço de voz online da Microsoft | LGPL-3.0 (biblioteca); serviço sujeito aos termos da Microsoft |
| Ollama + qwen2.5:7b / llama3.2:3b (PC mais fraco) | ollama.com / Alibaba Qwen / Meta | MIT / Apache-2.0 / Llama 3.2 Community License (uso comercial permitido; "Built with Llama") |
| Opcionais (não vêm no zip): Qwen3-TTS, Chatterbox, VoiceStudio | instalados à parte | Apache-2.0 / MIT / AGPL-3.0 |
| yt-dlp, ffmpeg | projetos livres | Unlicense / LGPL-GPL |

## Observações honestas
- Os mp4 de exemplo são vídeos de teste. Vários vídeos vão **só como projeto, sem mp4**, porque o vídeo original usava
  material que não pode ser redistribuído (trecho de trailer, recortes de vídeos de referência, música sem licença confirmada
  ou efeitos de um programa licenciado). O template e o `edit.json` estão lá para você renderizar com material seu.
- Algumas locuções de exemplo são a voz do autor do pacote ou vozes ElevenLabs dele: use só como exemplo, não republique.
- O vídeo 32 (Antártida, espanhol) tem roteiro modelado num vídeo de referência — é exemplo de técnica, não publique igual.
- Clipes de gameplay não vão no pacote — coloque os seus (livres) em `estoque/gameplay/`.
- `ESTILOS-*` só têm fichas de texto e links das referências — nenhum vídeo ou print de terceiros.
- O VoiceStudio/OmniVoice é programa de terceiros e **não** vem no pacote (só o link para instalar).
