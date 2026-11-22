// Kit Blender do Estúdio. Baseado no pipeline do kit cotidiano.explicado (mesmo autor)
/**
 * "Assa" o 3D de um vídeo para o Blender: monta a cena de cada quadro (a mesma
 * do modo rápido), anota onde cada peça está e grava tudo num .glb animado,
 * mais um .json com a câmera, o fundo e a luz de cada quadro.
 *
 * Roda no Node (sem navegador): é empacotado e chamado por scripts/blender/assar.mjs.
 */
import fs from 'node:fs';
import path from 'node:path';
import {act} from 'react';
import * as THREE from 'three';
import {createRoot, extend} from '@react-three/fiber';
import {GLTFExporter} from 'three/examples/jsm/exporters/GLTFExporter.js';
import * as CENA from '__CENA__';

type Registro = {mesh: THREE.Mesh; raio: number; quadros: Map<number, number[]>};

(globalThis as unknown as {IS_REACT_ACT_ENVIRONMENT: boolean}).IS_REACT_ACT_ENVIRONMENT = true;
// no Node o catálogo do three.js não vem registrado: registra tudo (<mesh>, <boxGeometry>…)
extend(THREE as unknown as Parameters<typeof extend>[0]);

// O GLTFExporter usa FileReader para o .glb; no Node não existe, então imitamos.
class LeitorDeArquivo {
  result: ArrayBuffer | string | null = null;
  onloadend: (() => void) | null = null;
  readAsArrayBuffer(b: Blob) {
    b.arrayBuffer().then((r) => {
      this.result = r;
      this.onloadend?.();
    });
  }
  readAsDataURL(b: Blob) {
    b.arrayBuffer().then((r) => {
      this.result = `data:${b.type};base64,${Buffer.from(r).toString('base64')}`;
      this.onloadend?.();
    });
  }
}
(globalThis as unknown as {FileReader: unknown}).FileReader = LeitorDeArquivo;

/** Um "renderizador" que não desenha nada: aqui só interessa a cena. */
const NADA: unknown = new Proxy(function () {}, {
  get: (_t, p) => (p === 'then' ? undefined : p === Symbol.toPrimitive ? () => 0 : NADA),
  apply: () => undefined,
});
const telaFalsa = {width: 1080, height: 1920, style: {}, addEventListener() {}, removeEventListener() {}, getContext: () => null, parentElement: null, clientWidth: 1080, clientHeight: 1920};
const glFalso = new Proxy(
  {render() {}, setSize() {}, setPixelRatio() {}, domElement: telaFalsa, shadowMap: {}, xr: {enabled: false, addEventListener() {}, removeEventListener() {}, isPresenting: false}},
  {get: (t, p) => (p in t ? (t as Record<string | symbol, unknown>)[p] : p === 'then' ? undefined : NADA)},
);

async function main() {
  const [id, saida] = process.argv.slice(2);
  const video = {quadro3D: CENA.quadro3D as (s: number) => any, duracao: CENA.DURACAO as number, pasta: id};

  const fps = 30;
  const total = Math.min(Math.round(video.duracao * fps), Number(process.env.QUADROS || 1e9));
  fs.mkdirSync(saida, {recursive: true});

  const root = createRoot(telaFalsa as unknown as HTMLCanvasElement);
  await root.configure({gl: glFalso as unknown as THREE.WebGLRenderer, size: {width: 1080, height: 1920, top: 0, left: 0}, frameloop: 'never', events: undefined, dpr: 1});

  const registros = new Map<string, Registro>();
  const quadros: {pos: number[]; alvo: number[]; fov: number; fundo: string; luz: number}[] = [];
  let cena: THREE.Scene | null = null;

  for (let f = 0; f < total; f++) {
    const q = video.quadro3D(f / fps);
    await act(async () => {
      const loja = root.render(<>{q.cena}</>);
      cena = loja.getState().scene;
    });
    quadros.push({pos: q.camera.pos, alvo: q.camera.alvo, fov: q.camera.fov, fundo: q.fundo, luz: q.luz ?? 1});
    const c = cena as unknown as THREE.Scene;
    c.updateMatrixWorld(true);
    c.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh) return;
      // só conta se ela e todos os "pais" estão visíveis
      for (let p: THREE.Object3D | null = o; p; p = p.parent) if (!p.visible) return;
      // a mesma peça pode trocar de tamanho a cada quadro (gota, fumaça): vira escala
      if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
      const raio = m.geometry.boundingSphere?.radius || 1;
      // mesma peça com outra forma (ex.: a boca trocando de sorriso para "o") vira outra peça
      const chave = `${m.uuid}:${m.geometry.type}`;
      let r = registros.get(chave);
      if (!r) {
        const mat = (Array.isArray(m.material) ? m.material[0] : m.material).clone() as unknown as Record<string, unknown>;
        // fora do navegador o R3F às vezes guarda a cor como texto ("#a9a6a0"): vira cor de verdade
        for (const k of ['color', 'emissive', 'specularColor', 'sheenColor', 'attenuationColor']) {
          const v = mat[k];
          if (typeof v === 'string' || typeof v === 'number') mat[k] = new THREE.Color(v as THREE.ColorRepresentation);
        }
        r = {mesh: new THREE.Mesh(m.geometry, mat as unknown as THREE.Material), raio, quadros: new Map()};
        registros.set(chave, r);
      }
      const k = raio / r.raio;
      const pos = new THREE.Vector3();
      const rot = new THREE.Quaternion();
      const esc = new THREE.Vector3();
      m.matrixWorld.decompose(pos, rot, esc);
      // peça com escala zero (ainda entrando) não tem giro: sem isso o giro vira NaN e o Blender recusa a cena
      if (![rot.x, rot.y, rot.z, rot.w].every(Number.isFinite)) rot.identity();
      const ok = (v: number) => (Number.isFinite(v) ? v : 0);
      r.quadros.set(f, [ok(pos.x), ok(pos.y), ok(pos.z), rot.x, rot.y, rot.z, rot.w, ok(esc.x * k), ok(esc.y * k), ok(esc.z * k)]);
    });
    if (process.env.QUADROS) console.log(`quadro ${f} ${Date.now()}`);
    else if (f % 30 === 0) process.stdout.write(`${Math.round((f / total) * 100)}% `);
  }

  // monta a cena final: uma peça por registro, com o caminho dela no tempo
  const final = new THREE.Scene();
  const trilhas: THREE.KeyframeTrack[] = [];
  let n = 0;
  for (const r of registros.values()) {
    const nome = `p${n++}`;
    r.mesh.name = nome;
    final.add(r.mesh);
    const tempos: number[] = [];
    const posicoes: number[] = [];
    const rotacoes: number[] = [];
    const escalas: number[] = [];
    let ultimo: number[] | null = null;
    for (let f = 0; f < total; f++) {
      const v = r.quadros.get(f);
      const atual = v ?? (ultimo ? [...ultimo.slice(0, 7), 0, 0, 0] : [0, -100, 0, 0, 0, 0, 1, 0, 0, 0]);
      if (v) ultimo = v;
      tempos.push(f / fps);
      posicoes.push(atual[0], atual[1], atual[2]);
      rotacoes.push(atual[3], atual[4], atual[5], atual[6]);
      escalas.push(atual[7], atual[8], atual[9]);
    }
    trilhas.push(new THREE.VectorKeyframeTrack(`${nome}.position`, tempos, posicoes, THREE.InterpolateDiscrete));
    trilhas.push(new THREE.QuaternionKeyframeTrack(`${nome}.quaternion`, tempos, rotacoes, THREE.InterpolateDiscrete));
    trilhas.push(new THREE.VectorKeyframeTrack(`${nome}.scale`, tempos, escalas, THREE.InterpolateDiscrete));
  }
  // tira os quadros repetidos (peças paradas ficam com poucos pontos)
  for (const t of trilhas) t.optimize();
  const clipe = new THREE.AnimationClip('cena', video.duracao, trilhas);

  const glb = (await new GLTFExporter().parseAsync(final, {binary: true, animations: [clipe]})) as ArrayBuffer;
  fs.writeFileSync(path.join(saida, 'cena.glb'), Buffer.from(glb));
  fs.writeFileSync(path.join(saida, 'quadros.json'), JSON.stringify({fps, total, pasta: video.pasta, quadros}));
  console.log(`\n${registros.size} peças, ${total} quadros → ${path.join(saida, 'cena.glb')}`);
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
