// Kit cotidiano.explicado · de cotidiano.explicado (@cotidiano.explicado) · não pode ser revendido nem usado para criar um produto parecido (LICENCA.md).
import type {PoseGato} from './Gato';
import {suave} from './tempo';

/** Gestos prontos do gato. Cada um devolve uma pose a partir do segundo atual. */

const lin = (s: number, t: number, d: number) => Math.min(1, Math.max(0, (s - t) / d));

/** Junta poses: a última manda; a cabeça soma. */
export const juntarGato = (...poses: PoseGato[]): PoseGato =>
  poses.reduce((a, p) => {
    const cab = a.cabeca && p.cabeca ? ([a.cabeca[0] + p.cabeca[0], a.cabeca[1] + p.cabeca[1]] as [number, number]) : p.cabeca ?? a.cabeca;
    return {...a, ...p, cabeca: cab};
  }, {} as PoseGato);

/** Quanto o olho está aberto: pisca uma vez a cada ~3,4 s. Use em `piscar`. */
export const piscadas = (s: number, fase = 0) => {
  const t = (s + fase) % 3.4;
  return t < 0.14 ? 1 - Math.sin((t / 0.14) * Math.PI) * 0.93 : 1;
};

/** Cavando com as patinhas da frente, uma de cada vez, entre `t0` e `t1`. */
export const cavar = (s: number, t0: number, t1: number, ritmo = 9): PoseGato => {
  const k = suave(lin(s, t0, 0.25)) * (1 - suave(lin(s, t1 - 0.25, 0.25)));
  if (k <= 0) return {};
  const a = 0.5 + 0.5 * Math.sin(s * ritmo);
  const b = 0.5 + 0.5 * Math.sin(s * ritmo + Math.PI);
  return {agacha: 0.6 * k, corpo: 0.14 * k, cabeca: [0.4 * k, 0], pataDE: k * (0.25 - 1.15 * a), pataDD: k * (0.25 - 1.15 * b), rabo: [Math.sin(s * ritmo * 0.5) * 0.4, 0.2], orelhas: 0.5};
};

/** Andando: patas em diagonal e rabinho balançando. `ritmo` = passos por segundo. */
export const andarGato = (s: number, ritmo = 1.6): PoseGato => {
  const a = s * ritmo * Math.PI * 2;
  return {pataDE: Math.sin(a) * 0.55, pataTD: Math.sin(a) * 0.55, pataDD: -Math.sin(a) * 0.55, pataTE: -Math.sin(a) * 0.55, rabo: [Math.sin(a * 0.5) * 0.25, 0.65], cabeca: [0, Math.sin(a * 0.5) * 0.06]};
};

/** Lambendo/limpando a patinha: levanta uma pata e abaixa a cabeça. */
export const limparPata = (s: number, t0: number, dur = 0.9, lado: 'D' | 'E' = 'D'): PoseGato => {
  const k = Math.sin(Math.PI * lin(s, t0, dur));
  const lamba = 0.12 * Math.sin((s - t0) * 22) * k;
  return {[lado === 'D' ? 'pataDD' : 'pataDE']: 0.9 * k + lamba, cabeca: [0.45 * k, (lado === 'D' ? -0.18 : 0.18) * k], corpo: 0.05 * k};
};
