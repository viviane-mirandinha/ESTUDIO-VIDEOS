import type {Pose} from './Personagem';

/**
 * Gestos prontos do personagem. Cada um devolve uma pose (só os ângulos que
 * ele mexe) a partir do segundo atual. Junte com `juntar(poseBase, gesto)`.
 *
 *   pose={juntar(POSE.parado, negar(s, quando('não deu certo')))}
 */

const limita = (x: number) => Math.min(1, Math.max(0, x));
/** Sobe e desce suave dentro da janela (0 fora dela). */
const janela = (s: number, t0: number, dur: number) => Math.sin(Math.PI * limita((s - t0) / dur));

/** Junta poses: a última manda; a cabeça soma (para gesto em cima de pose). */
export const juntar = (...poses: Pose[]): Pose =>
  poses.reduce((a, p) => {
    const cab = a.cabeca && p.cabeca ? ([a.cabeca[0] + p.cabeca[0], a.cabeca[1] + p.cabeca[1]] as [number, number]) : p.cabeca ?? a.cabeca;
    return {...a, ...p, cabeca: cab};
  }, {} as Pose);

/** Balança a cabeça dizendo "não" (use junto de um ✗). */
export const negar = (s: number, t0: number, dur = 1.3): Pose => ({cabeca: [0.05 * janela(s, t0, dur), Math.sin((s - t0) * 15) * 0.42 * janela(s, t0, dur)]});

/** Acena com a cabeça dizendo "sim" (use junto de um ✓). */
export const acenar = (s: number, t0: number, dur = 1.0): Pose => ({cabeca: [Math.sin((s - t0) * 13) * 0.22 * janela(s, t0, dur), 0]});

/** Ombros caídos e cabeça baixa (cansado, decepcionado). */
export const desanimar = (k: number): Pose => ({cabeca: [0.3 * k, 0], bracoE: [0.05, -0.05 * k], bracoD: [0.05, -0.05 * k], inclina: 0.12 * k});

/** Pulo de comemoração: braços para cima e o corpo sobe (`y` vai na posição). */
export const pular = (s: number, t0: number, vezes = 2, altura = 0.5): {pose: Pose; y: number} => {
  const t = s - t0;
  const ativo = t > 0 && t < vezes * 0.55;
  const y = ativo ? Math.abs(Math.sin((t / 0.55) * Math.PI)) * altura : 0;
  const k = limita(t / 0.2);
  return {
    pose: {bracoE: [0.3, 2.5 * k], bracoD: [0.3, 2.5 * k], cotoveloE: 0.3, cotoveloD: 0.3, cabeca: [-0.15 * k, 0], pernaE: -0.25 * (y / altura), pernaD: -0.25 * (y / altura), joelhoE: 0.5 * (y / altura), joelhoD: 0.5 * (y / altura)},
    y,
  };
};

/** Andando: pernas e braços alternados. `ritmo` = passos por segundo. */
export const andar = (s: number, ritmo = 1.8): Pose => {
  const a = s * ritmo * Math.PI;
  return {pernaE: Math.sin(a) * 0.5, pernaD: -Math.sin(a) * 0.5, joelhoE: Math.max(0, -Math.sin(a)) * 0.6, joelhoD: Math.max(0, Math.sin(a)) * 0.6, bracoE: [-Math.sin(a) * 0.4, 0.05], bracoD: [Math.sin(a) * 0.4, 0.05]};
};

/** Pedalando (use com a `Bicicleta` e o personagem sentado). `giro` = ângulo do pedal. */
export const pedalar = (giro: number): Pose => {
  const perna = (a: number) => ({p: 0.95 + 0.42 * Math.sin(a), j: 1.15 - 0.42 * Math.cos(a)});
  const e = perna(giro);
  const d = perna(giro + Math.PI);
  return {inclina: 0.35, bracoE: [1.15, 0.05], bracoD: [1.15, 0.05], cotoveloE: 0.25, cotoveloD: 0.25, pernaE: e.p, joelhoE: e.j, pernaD: d.p, joelhoD: d.j, cabeca: [-0.15, 0]};
};

/** Despejando com a mão direita (k: 0 segurando → 1 virado). Gire o objeto junto. */
export const despejar = (k: number): Pose => ({bracoD: [0.7 + 0.5 * k, 0.15], cotoveloD: 0.6 - 0.3 * k, cabeca: [0.15, 0.2]});

/** Poses paradas mais usadas. */
export const POSE: Record<'parado' | 'pensando' | 'apontando' | 'comemorando' | 'sentado' | 'dirigindo', Pose> = {
  parado: {bracoE: [0.05, 0.05], bracoD: [0.05, 0.05]},
  pensando: {bracoD: [2.0, 0.55], cotoveloD: 2.1, bracoE: [0.25, 0.05], cotoveloE: 0.3, cabeca: [0.08, 0.25]},
  apontando: {bracoD: [0.35, 1.35], cotoveloD: 0.05, bracoE: [0.05, 0.05], cabeca: [0, 0.6]},
  comemorando: {bracoE: [0.35, 2.45], bracoD: [0.35, 2.45], cotoveloE: 0.35, cotoveloD: 0.35, cabeca: [-0.18, 0]},
  sentado: {pernaE: 1.5, joelhoE: 1.5, pernaD: 1.5, joelhoD: 1.5},
  dirigindo: {inclina: -0.05, bracoE: [1.25, 0.1], bracoD: [1.25, 0.1], cotoveloE: 0.45, cotoveloD: 0.45, pernaE: 1.45, joelhoE: 1.35, pernaD: 1.45, joelhoD: 1.35},
};
