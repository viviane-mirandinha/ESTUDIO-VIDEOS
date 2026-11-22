import * as THREE from 'three';
import {mistura, suave} from './tempo';

export type V3 = [number, number, number];

/** Um enquadramento da câmera a partir do segundo `t`. */
export type Plano = {t: number; pos: V3; alvo: V3; fov?: number; /** quanto dura a deslizada até este plano (padrão: a de `cameraEm`) */ dur?: number};

export type Camera = {pos: V3; alvo: V3; fov: number};

const FOV = 32;

/**
 * Onde a câmera está no segundo `s`: desliza suave de um plano para o seguinte.
 * `dur` é quanto tempo leva cada deslizada (o resto do tempo ela só respira).
 */
export const cameraEm = (planos: Plano[], s: number, dur = 1.2): Camera => {
  let i = 0;
  while (i + 1 < planos.length && planos[i + 1].t <= s) i++;
  const atual = planos[i];
  const anterior = planos[Math.max(0, i - 1)];
  const k = i === 0 ? 1 : suave((s - atual.t) / (atual.dur ?? dur));
  const v = (a: V3, b: V3): V3 => [mistura(a[0], b[0], k), mistura(a[1], b[1], k), mistura(a[2], b[2], k)];
  // respiro: aproxima bem devagar enquanto o plano dura
  const respiro = Math.min(1, Math.max(0, s - atual.t) / 8) * 0.06;
  const pos = v(anterior.pos, atual.pos);
  const alvo = v(anterior.alvo, atual.alvo);
  const perto: V3 = [mistura(pos[0], alvo[0], respiro), mistura(pos[1], alvo[1], respiro), mistura(pos[2], alvo[2], respiro)];
  return {pos: perto, alvo, fov: mistura(anterior.fov ?? FOV, atual.fov ?? FOV, k)};
};

/** Monta uma câmera do three.js igual à da cena (para projetar pontos). */
export const cameraThree = (c: Camera, largura: number, altura: number) => {
  const cam = new THREE.PerspectiveCamera(c.fov, largura / altura, 0.1, 500);
  cam.position.set(...c.pos);
  cam.lookAt(...c.alvo);
  cam.updateMatrixWorld();
  cam.updateProjectionMatrix();
  return cam;
};

/**
 * Onde um ponto 3D cai na tela, em pixels. É assim que as etiquetas ficam
 * presas às peças: a cada quadro o ponto é projetado de novo.
 */
export const naTela = (c: Camera, ponto: V3, largura: number, altura: number) => {
  const v = new THREE.Vector3(...ponto).project(cameraThree(c, largura, altura));
  return {x: ((v.x + 1) / 2) * largura, y: ((1 - v.y) / 2) * altura, visivel: v.z < 1 && v.z > -1};
};
