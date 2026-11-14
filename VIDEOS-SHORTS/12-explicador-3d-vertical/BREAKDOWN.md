# 12 — Explicador 3D vertical (o que foi copiado do estilo)
Referências: @peraexplica, @explicandodireito.br, @garagemexplicativa, @thingsopened, @oclaud1n.
O yt-dlp não conseguiu listar os reels do Instagram (sem login, saída vazia). O estilo foi montado pelos prints que você mandou.

- Palco escuro (#0d0f15) com luz azulada no chão. Objeto 3D estilizado tipo massinha no centro: relógio de corda em latão, com bordas arredondadas e materiais foscos.
- Câmera sempre girando e chegando perto: relógio inteiro, mostrador abre, tambor com a mola, coroa, fila de engrenagens, escape, âncora, volante, espiral, rubis. No fim ela se afasta e o mostrador fecha.
- Rótulos em pílula com haste apontando a peça, nas cores branca, amarela e vermelha: "0 BATERIA", "MOLA REAL", "COROA", "ESCAPE", "1 DENTE POR VEZ", "8x POR SEGUNDO", "~40 HORAS"…
- Legenda GRANDE (Montserrat Black 96px, caixa alta), branca com contorno preto e 1 palavra-chave em amarelo. Até 3 palavras por vez.
- Cabeçalho pequeno no topo: "@explica.em3d · RELÓGIO DE CORDA". O perfil é inventado, não copia nenhum dos perfis de referência.
- Mecânica animada de verdade:
  - a mola aperta quando a coroa gira e solta aos poucos;
  - a relação entre as engrenagens segue os raios;
  - a roda de escape avança 1 dente a cada meia oscilação do volante;
  - a âncora trava e destrava e o espiral "respira";
  - em "Se nada segurasse", a âncora sai, o volante para e a mola desenrola num instante;
  - em "oito vezes por segundo", o volante passa a 4 Hz reais (8 alternâncias/s). No resto do vídeo ele anda em câmera lenta.
- Reaproveitado: `_template-palco3d` (palco.py + base.html, com câmera, rótulos ancorados e legenda). Por cima vai uma camada CSS do estilo 12, aplicada em gerar_edit.py. O base.html compartilhado não foi alterado.
