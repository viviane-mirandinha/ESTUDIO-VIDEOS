/**
 * Curvas de animação. Toda animação do kit sai daqui e depende só do segundo
 * atual — nunca do relógio.
 */

const limita = (x: number) => Math.min(1, Math.max(0, x));

/** Começa rápido e freia no fim (para coisas que entram). */
export const freia = (x: number) => 1 - Math.pow(1 - limita(x), 3);
/** Acelera e freia (para movimentos de câmera). */
export const suave = (x: number) => {
  const k = limita(x);
  return k * k * (3 - 2 * k);
};
/** Passa um pouco do ponto e volta (pulo de entrada de etiqueta). */
export const mola = (x: number) => {
  const k = limita(x);
  const c = 1.9;
  return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2);
};

/** 0 → 1 entre `t0` e `t0 + dur`, com a curva escolhida. */
export const desde = (s: number, t0: number, dur = 0.4, curva: (x: number) => number = freia) => curva((s - t0) / dur);

/** 1 enquanto está no ar, entrando em `t0` e saindo em `t1` (se tiver). */
export const noAr = (s: number, t0: number, t1?: number, entra = 0.3, sai = 0.25) => {
  const k = desde(s, t0, entra);
  return t1 === undefined ? k : k * (1 - desde(s, t1 - sai, sai, suave));
};

/** Mistura de dois números. */
export const mistura = (a: number, b: number, k: number) => a + (b - a) * k;

/** Palavra da fala: texto, início e fim em segundos. */
export type Palavra = {w: string; i: number; f: number};

/**
 * Segundo em que um trecho começa a ser falado. Procura as palavras em ordem
 * (ignora acento e pontuação). `depois` pula ocorrências anteriores a esse segundo.
 */
export const criarQuando = (palavras: Palavra[]) => {
  const limpa = (t: string) =>
    t
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9 ]/g, '')
      .trim();
  const lista = palavras.map((p) => ({...p, l: limpa(p.w)}));
  return (trecho: string, depois = 0): number => {
    const alvo = limpa(trecho).split(/\s+/);
    for (let i = 0; i < lista.length; i++) {
      if (lista[i].i < depois) continue;
      if (alvo.every((a, j) => lista[i + j]?.l === a)) return lista[i].i;
    }
    throw new Error(`Trecho não encontrado na fala: "${trecho}"`);
  };
};

type V3 = [number, number, number];

/**
 * Peça indo até o lugar dela e encaixando: viaja de `de` até `para` em `dur`
 * segundos, freia no fim e dá um pequeno tranco ao assentar.
 */
export const encaixar = (s: number, t0: number, dur: number, de: V3, para: V3): V3 => {
  const k = Math.min(1, Math.max(0, (s - t0) / dur));
  const e = 1 - Math.pow(1 - k, 3);
  const assenta = s > t0 + dur ? Math.exp(-(s - t0 - dur) * 18) * Math.sin((s - t0 - dur) * 40) * 0.03 : 0;
  return [mistura(de[0], para[0], e), mistura(de[1], para[1], e) - assenta, mistura(de[2], para[2], e)];
};

/** Tremedeira de motor ligando: deslocamento pequeno entre t0 e t1 (forte no começo). */
export const tremer = (s: number, t0: number, t1: number, forca = 0.04): V3 => {
  if (s < t0 || s > t1) return [0, 0, 0];
  const k = 1 - (s - t0) / (t1 - t0);
  const f = forca * (0.35 + 0.65 * k);
  return [Math.sin(s * 71) * f * 0.5, Math.sin(s * 93 + 1) * f, Math.sin(s * 57 + 2) * f * 0.5];
};
