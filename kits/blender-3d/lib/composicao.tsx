import React from 'react';
import {Personagem} from './Personagem';
import type {Acessorios, Barba, Cabelo, Cores, Estilo, Expressao, Pose, Roupa} from './Personagem';
import {PERSONAGEM_KIRMASK} from './personagemPadrao';
import {Gato} from './Gato';
import {ALCA_GALAO, CarroDetalhado, Galao} from './Objetos';
import {Atelie, Garagem, Infinito} from './Cenarios';
import {cameraEm} from './camera';
import type {Plano, V3} from './camera';
import {POSE, andar, despejar, juntar} from './gestos';
import {suave} from './tempo';
import type {Quadro3D} from './tipos';

/**
 * Compõe uma cena 3D a partir de um PLANO DE CENAS (plano.json): cada cena diz o cenário, a pose e a
 * expressão do personagem, o objeto em cena e o enquadramento da câmera. É o que o "modo grátis" usa:
 * o plano pode ser escrito por um modelo local (Ollama) ou à mão, sem escrever código 3D.
 */

export type Cenario = 'garagem' | 'atelie' | 'infinito' | 'nenhum';
export type PoseNome = 'parado' | 'pensando' | 'apontando' | 'comemorando' | 'andando';
export type ObjetoNome = 'nenhum' | 'carro' | 'galao' | 'gato';
export type Enquadramento = 'geral' | 'medio' | 'close' | 'lado' | 'alto';
export type Lado = 'esq' | 'centro' | 'dir';

/** Visual do personagem (tudo opcional; o que faltar vem do personagem padrão). */
export type PersonagemConfig = {
  estilo?: Estilo;
  roupa?: Roupa;
  cabelo?: Cabelo;
  barba?: Barba;
  acessorios?: Acessorios;
  cores?: Partial<Cores>;
  escala?: number;
  rostoNovo?: boolean;
};

export type CenaPlano = {
  id: number;
  /** segundos em que a cena começa e termina */
  de: number;
  ate: number;
  texto?: string;
  cenario?: Cenario;
  fundo?: string;
  luz?: number;
  pose?: PoseNome;
  expressao?: Expressao;
  objeto?: ObjetoNome;
  enquadramento?: Enquadramento;
  lado?: Lado;
  /** outro ponto (x) que precisa caber no quadro junto do personagem, ex.: um modelo .glb importado ao lado */
  alvo_x?: number;
  /** muda o visual do personagem só nesta cena (ex.: outra roupa) */
  personagem?: PersonagemConfig;
  /** esconde o personagem do kit (a cena usa só modelos .glb importados) */
  sem_personagem?: boolean;
};
export type PlanoVideo = {cenas: CenaPlano[]; personagem?: PersonagemConfig; render?: Record<string, unknown>};
export type Palavra = {w?: string; s: number; e: number};

export const CENARIOS: Record<Cenario, {fundo: string; luz: number}> = {
  garagem: {fundo: '#3d424b', luz: 1.3},
  atelie: {fundo: '#e9dccb', luz: 1.15},
  infinito: {fundo: '#f2dcc2', luz: 1.1},
  nenhum: {fundo: '#f2dcc2', luz: 1.1},   // o ambiente é montado no Blender (ambiente.json)
};

const PX: Record<Lado, number> = {esq: -1.5, centro: 0, dir: 1.5};
const PZ = 0.9;
const GIRO: Record<Lado, number> = {esq: 0.5, centro: 0.15, dir: -0.5};

/** Onde fica o objeto principal em relação ao personagem (do lado oposto). */
const posObjeto = (lado: Lado): {x: number; z: number; giro: number} => (lado === 'dir' ? {x: -2.0, z: -1.2, giro: 0.55} : {x: 2.0, z: -1.2, giro: -0.55});

const GATO_DX = 1.6;

/** Câmera para um enquadramento. No vídeo vertical cabe pouca largura: a distância cresce com o que precisa aparecer. */
const enquadrar = (tipo: Enquadramento, lado: Lado, objeto: ObjetoNome, alvoX?: number): Omit<Plano, 't'> => {
  const px = PX[lado];
  const ox = alvoX !== undefined ? alvoX : objeto === 'carro' ? posObjeto(lado).x : objeto === 'gato' ? px + (lado === 'dir' ? -GATO_DX : GATO_DX) : px;
  const cx = (px + ox) / 2;
  // largura vertical 9:16: a visão horizontal vale 0,3226 × a distância (fov 32)
  const dist = Math.min(18, Math.max(9, (Math.abs(px - ox) + 3.2) / 0.3226));
  switch (tipo) {
    case 'close':
      return {pos: [px + 0.4, 2.4, PZ + 4.4], alvo: [px, 2.15, PZ], fov: 30};
    case 'medio':
      // com objeto (carro, gato) o plano médio abre o suficiente para os dois aparecerem
      if (ox !== px) return {pos: [cx + 0.4, 2.6, PZ + Math.max(7, dist * 0.8)], alvo: [cx, 1.8, PZ], fov: 32};
      return {pos: [px + 0.4, 2.5, PZ + 6.2], alvo: [px, 2.1, PZ], fov: 32};
    case 'lado':
      return {pos: [cx + dist * 0.8, 2.6, PZ + dist * 0.55], alvo: [cx, 1.6, PZ - 0.3], fov: 32};
    case 'alto':
      return {pos: [cx + 0.6, 4 + dist * 0.35, PZ + dist * 0.8], alvo: [cx, 1.0, PZ], fov: 34};
    default:
      return {pos: [cx + 0.4, 2.8, PZ + dist], alvo: [cx, 1.5, PZ], fov: 32};
  }
};

const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
/** Mistura duas poses (números e pares de números); o que faltar conta como 0. */
const misturaPose = (a: Pose, b: Pose, k: number): Pose => {
  const r: Record<string, unknown> = {};
  for (const chave of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const va = (a as Record<string, unknown>)[chave];
    const vb = (b as Record<string, unknown>)[chave];
    if (Array.isArray(va ?? vb)) {
      const x = (va as number[] | undefined) ?? [0, 0];
      const y = (vb as number[] | undefined) ?? [0, 0];
      r[chave] = [lerp(x[0], y[0], k), lerp(x[1], y[1], k)];
    } else r[chave] = lerp((va as number | undefined) ?? 0, (vb as number | undefined) ?? 0, k);
  }
  return r as Pose;
};

const poseDe = (nome: PoseNome, s: number, objeto: ObjetoNome): Pose => {
  const base = nome === 'andando' ? juntar(POSE.parado, andar(s)) : POSE[nome];
  // com o galão na mão direita, o braço fica levantado para segurá-lo
  return objeto === 'galao' && nome !== 'comemorando' ? juntar(base, despejar(0)) : base;
};

/** Boca no ritmo da fala: abre e fecha enquanto há uma palavra sendo dita. */
const juntaPersonagem = (...cfgs: (PersonagemConfig | undefined)[]) => {
  let r: Required<Pick<PersonagemConfig, 'cores' | 'acessorios'>> & PersonagemConfig = {...PERSONAGEM_KIRMASK, cores: {}, acessorios: {}};
  r = {...r, cores: {...PERSONAGEM_KIRMASK.cores}, acessorios: {...PERSONAGEM_KIRMASK.acessorios}};
  for (const c of cfgs) {
    if (!c) continue;
    r = {...r, ...c, cores: {...r.cores, ...(c.cores ?? {})}, acessorios: {...r.acessorios, ...(c.acessorios ?? {})}};
  }
  return r;
};

const falaEm = (s: number, palavras: Palavra[]): number => {
  for (const p of palavras) {
    if (s >= p.s && s <= p.e) return 0.3 + 0.7 * Math.abs(Math.sin((s - p.s) * 13));
  }
  return 0;
};

export const criarCena = (plano: PlanoVideo, palavras: Palavra[] = []) => {
  const cenas = [...plano.cenas].sort((a, b) => a.de - b.de);
  const duracao = cenas.length ? Math.max(...cenas.map((c) => c.ate)) : 1;
  const cam: Plano[] = cenas.map((c) => ({t: c.de, ...enquadrar(c.enquadramento ?? 'medio', c.lado ?? 'centro', c.objeto ?? 'nenhum', c.alvo_x)}));
  const indice = (s: number) => {
    let i = 0;
    while (i + 1 < cenas.length && cenas[i + 1].de <= s) i++;
    return i;
  };

  const quadro3D = (s: number): Quadro3D => {
    const i = indice(s);
    const c = cenas[i];
    const ant = cenas[Math.max(0, i - 1)];
    const lado = c.lado ?? 'centro';
    const objeto = c.objeto ?? 'nenhum';
    const cenario = c.cenario ?? 'garagem';
    const padrao = CENARIOS[cenario];
    // a pose entra suave a partir da anterior (meio segundo) e o corpo "respira" por cima
    const k = i === 0 ? 1 : suave((s - c.de) / 0.5);
    const nova = poseDe(c.pose ?? 'parado', s, objeto);
    const velha = poseDe(ant.pose ?? 'parado', s, ant.objeto ?? 'nenhum');
    const pose = juntar(misturaPose(velha, nova, k), {inclina: (misturaPose(velha, nova, k).inclina ?? 0) + 0.012 * Math.sin(s * 2), cabeca: [0.02 * Math.sin(s * 1.3), 0.05 * Math.sin(s * 0.8)]});
    const px = PX[lado];
    const naMao: [number, number, number] = [-ALCA_GALAO[0], -0.06 - ALCA_GALAO[1], -ALCA_GALAO[2]];
    const o = posObjeto(lado);
    return {
      camera: cameraEm(cam, s, 0.9),
      fundo: c.fundo ?? padrao.fundo,
      luz: c.luz ?? padrao.luz,
      cena: (
        <>
          {cenario === 'nenhum' ? null : cenario === 'garagem' ? <Garagem /> : cenario === 'atelie' ? <Atelie /> : <Infinito cor={c.fundo ?? padrao.fundo} />}
          {c.sem_personagem ? null : <Personagem
            {...juntaPersonagem(plano.personagem, c.personagem)}
            position={[px, 0, PZ]}
            rotation={[0, GIRO[lado], 0]}
            pose={pose}
            expressao={c.expressao ?? 'feliz'}
            tempo={s}
            fala={falaEm(s, palavras)}
            naMao={objeto === 'galao' ? <group position={naMao}><Galao /></group> : null}
          />}
          {objeto === 'carro' ? (
            <group position={[o.x, 0, o.z]} rotation={[0, o.giro, 0]}>
              <CarroDetalhado />
            </group>
          ) : null}
          {objeto === 'gato' ? <Gato position={[px + (lado === 'dir' ? -GATO_DX : GATO_DX), 0, PZ + 1.0]} rotation={[0, lado === 'dir' ? 0.8 : -0.8, 0]} expressao="curioso" pose={{senta: 1, rabo: [0.2 * Math.sin(s * 3), 0.5]}} /> : null}
        </>
      ),
    };
  };

  return {duracao, quadro3D};
};
