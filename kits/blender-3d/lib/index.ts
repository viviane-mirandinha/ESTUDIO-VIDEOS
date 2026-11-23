// Biblioteca de peças 3D do kit Blender do Estúdio (personagem, objetos, cenários, câmera, tempo).
// Tudo aqui é puro three.js / React Three Fiber: nada depende do Remotion nem de outra pasta.
export * from './tempo';
export * from './camera';
export type {Quadro3D} from './tipos';
export {Personagem, pontoNaMao} from './Personagem';
export type {Estilo, Roupa, Cabelo, Barba, Acessorios, Pose, Cores, Expressao} from './Personagem';
export {PERSONAGEM_KIRMASK, PERSONAGEM_KIRMASK as PERSONAGEM_PADRAO} from './personagemPadrao';
export * from './gestos';
export {Gato, GATO_LARANJA, GATO_CINZA} from './Gato';
export type {PoseGato, ExpressaoGato, CoresGato} from './Gato';
export * from './gestosGato';
export {CarroDetalhado, BAIA_MOTOR, Galao, bicoDoGalao, ALCA_GALAO, Vasilha, Fogo, Fumaca, JatoLiquido, Bicicleta, Volante} from './Objetos';
export {BicicletaPedal, EIXO_PEDAL, pedalEm} from './BicicletaPedal';
export {Turbina} from './Turbina';
export {MotorCorte, MOTOR_ALTERNADOR, MOTOR_BATERIA} from './MotorCorte';
export type {FocoMotor} from './MotorCorte';
export {Garagem,Atelie, Infinito} from './Cenarios';
export {criarCena, CENARIOS} from './composicao';
export type {PersonagemConfig, PlanoVideo, CenaPlano, Palavra, Cenario, PoseNome, ObjetoNome, Enquadramento, Lado} from './composicao';
