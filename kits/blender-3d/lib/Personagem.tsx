// Kit cotidiano.explicado · de cotidiano.explicado (@cotidiano.explicado) · não pode ser revendido nem usado para criar um produto parecido (LICENCA.md).
import React, {createContext, useContext, useMemo} from 'react';
import * as THREE from 'three';

/**
 * O personagem do kit, montado com formas simples (sem modelo de fora).
 *
 * Estilos de acabamento:
 * - `vinil` (padrão do Kit cotidiano.explicado): brinquedo de vinil brilhante, cabeça grande.
 * - `massinha`: tudo fosco e arredondado.
 * - `desenho`: sombra em degraus e contorno preto.
 *
 * Roupa, cabelo, cores e pose vêm por props. A pose é só ângulos — anime
 * mudando os ângulos a partir do quadro atual.
 */

export type Estilo = 'massinha' | 'vinil' | 'desenho';
export type Roupa = 'camiseta' | 'moletom' | 'jardineira' | 'jaqueta' | 'varsity';
export type Cabelo = 'tigela' | 'topete' | 'cacheado' | 'mullet';
export type Barba = 'nenhuma' | 'cavanhaque';
/** Expressão do rosto (olhos, sobrancelhas e boca mudam juntos). */
export type Expressao = 'feliz' | 'orgulhoso' | 'triste' | 'surpreso' | 'cansado' | 'bravo' | 'pensativo' | 'animado';

/** Como cada expressão mexe no rosto. */
const ROSTO: Record<Expressao, {olhoY: number; olhoEsc: number; sobY: number; sobGiro: number; boca: 'sorriso' | 'sorrisao' | 'triste' | 'o' | 'reta'}> = {
  feliz: {olhoY: 1, olhoEsc: 1, sobY: 0, sobGiro: 0.12, boca: 'sorriso'},
  animado: {olhoY: 1.12, olhoEsc: 1.08, sobY: 0.1, sobGiro: 0.12, boca: 'sorrisao'},
  orgulhoso: {olhoY: 0.55, olhoEsc: 1, sobY: 0.02, sobGiro: 0.12, boca: 'sorrisao'},
  triste: {olhoY: 0.85, olhoEsc: 0.95, sobY: 0.04, sobGiro: -0.38, boca: 'triste'},
  surpreso: {olhoY: 1.2, olhoEsc: 1.15, sobY: 0.12, sobGiro: 0.05, boca: 'o'},
  cansado: {olhoY: 0.42, olhoEsc: 1, sobY: -0.03, sobGiro: -0.25, boca: 'reta'},
  bravo: {olhoY: 0.8, olhoEsc: 1, sobY: -0.05, sobGiro: 0.45, boca: 'triste'},
  pensativo: {olhoY: 0.9, olhoEsc: 1, sobY: 0.05, sobGiro: -0.15, boca: 'reta'},
};
/** Detalhes opcionais do visual. */
export type Acessorios = {brinco?: boolean; tatuagem?: boolean; bolsa?: boolean; bolsosCargo?: boolean; cadarcos?: boolean};

export type Pose = {
  /** Braço esquerdo/direito: [frente/trás, abre/fecha] em radianos. */
  bracoE?: [number, number];
  bracoD?: [number, number];
  cotoveloE?: number;
  cotoveloD?: number;
  /** Cabeça: [inclina para frente, vira para os lados]. */
  cabeca?: [number, number];
  /** Pernas: frente/trás. */
  pernaE?: number;
  pernaD?: number;
  /** Joelhos: quanto a canela dobra para trás (π/2 = sentado). */
  joelhoE?: number;
  joelhoD?: number;
  /** Corpo inteiro: inclina para frente (radianos). */
  inclina?: number;
};

export type Cores = {
  pele: string;
  /** Peça de cima (camiseta, moletom, jaqueta ou a jardineira). */
  roupa: string;
  /** Camiseta que aparece por baixo (jardineira e jaqueta). */
  baixo: string;
  calca: string;
  tenis: string;
  sola: string;
  cabelo: string;
  /** Listras da gola, punhos e barra (jaqueta varsity). */
  listraA: string;
  listraB: string;
  cadarco: string;
};

export const CORES_PADRAO: Cores = {
  pele: '#f0c39c',
  roupa: '#ece7dd',
  baixo: '#ffffff',
  calca: '#5b6b3f',
  tenis: '#f7f7f5',
  sola: '#2b2b30',
  cabelo: '#3b2418',
  listraA: '#c8332b',
  listraB: '#1d2a4a',
  cadarco: '#ffffff',
};

const usaDegraus = () =>
  useMemo(() => {
    const dados = new Uint8Array([90, 170, 255]);
    const t = new THREE.DataTexture(dados, 3, 1, THREE.RedFormat);
    t.minFilter = THREE.NearestFilter;
    t.magFilter = THREE.NearestFilter;
    t.needsUpdate = true;
    return t;
  }, []);

const Mat: React.FC<{cor: string; estilo: Estilo; degraus: THREE.Texture; fosco?: boolean}> = ({cor, estilo, degraus, fosco}) => {
  if (estilo === 'vinil') return <meshPhysicalMaterial color={cor} roughness={fosco ? 0.6 : 0.28} clearcoat={fosco ? 0.3 : 1} clearcoatRoughness={0.15} />;
  if (estilo === 'desenho') return <meshToonMaterial color={cor} gradientMap={degraus} />;
  return <meshStandardMaterial color={cor} roughness={0.92} />;
};

type V = [number, number, number];

/**
 * Giro acumulado do tronco + braço + antebraço. O que vai na mão recebe o giro
 * contrário: assim um galão continua em pé (alinhado com o corpo) mesmo com o
 * braço levantado, e só inclina quando a cena manda.
 */
const giroDoBraco = (lado: 1 | -1, ang: [number, number] = [0, 0], cotovelo = 0, inclina = 0) =>
  new THREE.Quaternion()
    .setFromEuler(new THREE.Euler(inclina, 0, 0))
    .multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(-ang[0], 0, lado * (0.12 + ang[1]))))
    .multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(-cotovelo, 0, 0)));

/**
 * Onde um ponto do que está na mão direita (`local`, nas coordenadas do objeto
 * na mão) fica no mundo. Use para prender um jato, uma etiqueta ou uma faísca
 * no bico de um galão, na ponta de uma ferramenta etc.
 */
export const pontoNaMao = (p: {position?: V; rotation?: V; escala?: number; pose?: Pose}, local: V = [0, 0, 0]): V => {
  const pose = p.pose ?? {};
  const ang = pose.bracoD ?? [0, 0];
  const cot = pose.cotoveloD ?? 0;
  const inc = pose.inclina ?? 0;
  const M = (pos: V, q: THREE.Quaternion = new THREE.Quaternion(), e = 1) => new THREE.Matrix4().compose(new THREE.Vector3(...pos), q, new THREE.Vector3(e, e, e));
  const R = (x: number, y: number, z: number) => new THREE.Quaternion().setFromEuler(new THREE.Euler(x, y, z));
  const m = M(p.position ?? [0, 0, 0], R(...(p.rotation ?? [0, 0, 0])), p.escala ?? 1)
    .multiply(M([0, 0.86, 0], R(inc, 0, 0)))
    .multiply(M([0, -0.86, 0]))
    .multiply(M([0.42, 1.58, 0], R(-ang[0], 0, 0.12 + ang[1])))
    .multiply(M([0, -0.36, 0], R(-cot, 0, 0)))
    .multiply(M([0, -0.5, 0], giroDoBraco(1, ang, cot, inc).invert()));
  const v = new THREE.Vector3(...local).applyMatrix4(m);
  return [v.x, v.y, v.z];
};

/** Estilo e textura compartilhados pelas peças de um personagem. */
const Acabamento = createContext<{estilo: Estilo; degraus: THREE.Texture | null}>({estilo: 'vinil', degraus: null});

/**
 * Uma peça do corpo; no estilo desenho ganha contorno preto por trás.
 * Fica fora do Personagem de propósito: criada dentro, o React remontaria o
 * corpo inteiro a cada quadro.
 */
const Peca: React.FC<{cor: string; pos?: V; rot?: V; esc?: V; fosco?: boolean; children: React.ReactElement}> = ({cor, pos, rot, esc, fosco, children}) => {
  const {estilo, degraus} = useContext(Acabamento);
  return (
    <group position={pos} rotation={rot} scale={esc}>
      <mesh castShadow receiveShadow>
        {children}
        <Mat cor={cor} estilo={estilo} degraus={degraus as THREE.Texture} fosco={fosco} />
      </mesh>
      {estilo === 'desenho' ? (
        <mesh scale={1.06}>
          {children}
          <meshBasicMaterial color="#141414" side={THREE.BackSide} />
        </mesh>
      ) : null}
    </group>
  );
};

export const Personagem: React.FC<{
  estilo?: Estilo;
  roupa?: Roupa;
  cabelo?: Cabelo;
  barba?: Barba;
  acessorios?: Acessorios;
  cores?: Partial<Cores>;
  pose?: Pose;
  position?: V;
  rotation?: V;
  escala?: number;
  /** O que ele segura na mão direita (fica preso à mão). */
  naMao?: React.ReactNode;
  /** Expressão do rosto. */
  expressao?: Expressao;
  /** Suor (0 → 1): gotas escorrendo da testa. Precisa de `tempo`. */
  suor?: number;
  /** Segundo atual (para o suor escorrer). */
  tempo?: number;
  /** Boca falando (0 → 1): abre a boca no ritmo da voz, por cima da expressão. */
  fala?: number;
  /** Olhos embutidos no rosto, maiores e com brilho (não saltam para fora de perfil). */
  rostoNovo?: boolean;
}> = ({estilo = 'vinil', roupa = 'moletom', cabelo = 'topete', barba = 'nenhuma', acessorios = {}, cores, pose = {}, position, rotation, escala = 1, naMao, expressao = 'feliz', suor = 0, tempo = 0, fala = 0, rostoNovo = false}) => {
  const rosto = ROSTO[expressao];
  const c = {...CORES_PADRAO, ...cores};
  const degraus = usaDegraus();


  const R = estilo === 'vinil' ? 0.62 : 0.52;
  const [cabX, cabY] = pose.cabeca ?? [0, 0];
  const mangaLonga = roupa === 'moletom' || roupa === 'jaqueta' || roupa === 'varsity';
  const varsity = roupa === 'varsity';
  const corManga = roupa === 'jardineira' ? c.baixo : c.roupa;
  const tecido = roupa === 'moletom' || roupa === 'jardineira' || varsity;
  /** Faixa listrada (gola, punho, barra): três anéis empilhados. */
  const listras = [c.listraB, c.listraA, c.baixo, c.listraA, c.listraB];

  const braco = (lado: 1 | -1, ang: [number, number] = [0, 0], cotovelo = 0, mao?: React.ReactNode) => (
    <group position={[0.42 * lado, 1.58, 0]} rotation={[-ang[0], 0, lado * (0.12 + ang[1])]}>
      <Peca cor={corManga} pos={[0, -0.14, 0]} fosco={tecido}>
        <capsuleGeometry args={[0.15, 0.16, 8, 16]} />
      </Peca>
      <group position={[0, -0.36, 0]} rotation={[-cotovelo, 0, 0]}>
        <Peca cor={mangaLonga ? c.roupa : c.pele} pos={[0, -0.17, 0]} fosco={mangaLonga && tecido}>
          <capsuleGeometry args={[mangaLonga ? 0.135 : 0.11, 0.26, 8, 16]} />
        </Peca>
        {varsity ? (
          // punho listrado
          listras.map((cor, i) => (
            <Peca key={i} cor={cor} pos={[0, -0.29 - i * 0.022, 0]} fosco>
              <cylinderGeometry args={[0.125, 0.125, 0.024, 20]} />
            </Peca>
          ))
        ) : mangaLonga ? (
          // punho
          <Peca cor={c.roupa} pos={[0, -0.33, 0]} fosco={tecido}>
            <cylinderGeometry args={[0.12, 0.12, 0.06, 20]} />
          </Peca>
        ) : null}
        <Peca cor={c.pele} pos={[0, -0.42, 0]}>
          <sphereGeometry args={[0.13, 20, 16]} />
        </Peca>
        {mao ? (
          <group position={[0, -0.5, 0]} quaternion={giroDoBraco(lado, ang, cotovelo, pose.inclina ?? 0).invert()}>
            {mao}
          </group>
        ) : null}
      </group>
    </group>
  );

  const perna = (lado: 1 | -1, ang = 0, joelho = 0) => (
    <group position={[0.17 * lado, 0.86, 0]} rotation={[-ang, 0, 0]}>
      {/* coxa */}
      <Peca cor={roupa === 'jardineira' ? c.roupa : c.calca} pos={[0, -0.18, 0]} fosco>
        <capsuleGeometry args={[0.15, 0.2, 8, 16]} />
      </Peca>
      {acessorios.bolsosCargo ? (
        // bolso lateral da calça cargo
        <Peca cor={c.calca} pos={[0.13 * lado, -0.24, 0.02]} esc={[0.5, 1, 1]} fosco>
          <boxGeometry args={[0.12, 0.2, 0.2]} />
        </Peca>
      ) : null}
      {/* joelho para baixo: canela e tênis dobram juntos */}
      <group position={[0, -0.36, 0]} rotation={[joelho, 0, 0]}>
        <Peca cor={roupa === 'jardineira' ? c.roupa : c.calca} pos={[0, -0.16, 0]} fosco>
          <capsuleGeometry args={[0.145, 0.18, 8, 16]} />
        </Peca>
        {/* tênis: cabedal e sola */}
        <Peca cor={c.tenis} pos={[0, -0.36, 0.08]} esc={[1, 0.62, 1.45]}>
          <sphereGeometry args={[0.17, 24, 16]} />
        </Peca>
        <Peca cor={c.sola} pos={[0, -0.44, 0.08]} esc={[1.05, 0.22, 1.5]}>
          <sphereGeometry args={[0.17, 24, 12]} />
        </Peca>
        {acessorios.cadarcos
          ? [0, 1, 2].map((i) => (
              // cadarços grossos atravessados no peito do pé
              <Peca key={i} cor={c.cadarco} pos={[0, -0.28 - i * 0.012, 0.12 + i * 0.06]} rot={[0.5, 0, 0]}>
                <boxGeometry args={[0.2, 0.035, 0.05]} />
              </Peca>
            ))
          : null}
      </group>
    </group>
  );

  const tronco = (
    <group position={[0, 1.26, 0]}>
      <Peca cor={roupa === 'jardineira' ? c.baixo : c.roupa} esc={[1, 1, 0.78]} fosco={tecido}>
        <capsuleGeometry args={[0.36, 0.5, 10, 24]} />
      </Peca>
      {roupa === 'moletom' ? (
        <>
          {/* bolso canguru e cordões */}
          <Peca cor={c.roupa} pos={[0, -0.22, 0.27]} esc={[1, 0.55, 0.22]} fosco>
            <sphereGeometry args={[0.26, 24, 16]} />
          </Peca>
          {[-1, 1].map((l) => (
            <Peca key={l} cor="#d8d2c6" pos={[l * 0.08, 0.2, 0.3]} rot={[0.15, 0, 0]}>
              <cylinderGeometry args={[0.018, 0.018, 0.24, 8]} />
            </Peca>
          ))}
          {/* capuz caído nas costas */}
          <Peca cor={c.roupa} pos={[0, 0.42, -0.18]} rot={[1.2, 0, 0]} esc={[1, 1, 0.7]} fosco>
            <torusGeometry args={[0.26, 0.11, 14, 28]} />
          </Peca>
        </>
      ) : null}
      {roupa === 'jardineira' ? (
        <>
          {/* peitilho e alças */}
          <Peca cor={c.roupa} pos={[0, -0.08, 0.2]} esc={[1, 1, 0.5]} fosco>
            <boxGeometry args={[0.46, 0.42, 0.2]} />
          </Peca>
          <Peca cor={c.roupa} pos={[0, -0.42, 0]} esc={[1, 0.6, 0.8]} fosco>
            <sphereGeometry args={[0.37, 24, 16]} />
          </Peca>
          {[-1, 1].map((l) => (
            <Peca key={l} cor={c.roupa} pos={[l * 0.17, 0.26, 0.04]} rot={[0.2, 0, 0]} fosco>
              <boxGeometry args={[0.08, 0.36, 0.62]} />
            </Peca>
          ))}
          {[-1, 1].map((l) => (
            <Peca key={`b${l}`} cor="#d9b45a" pos={[l * 0.17, 0.08, 0.3]}>
              <cylinderGeometry args={[0.035, 0.035, 0.03, 12]} />
            </Peca>
          ))}
        </>
      ) : null}
      {varsity ? (
        <>
          {/* camiseta branca no meio da jaqueta aberta e os botões de pressão */}
          <Peca cor={c.baixo} pos={[0, -0.02, 0.27]} esc={[1, 1, 0.4]} fosco>
            <boxGeometry args={[0.26, 0.82, 0.1]} />
          </Peca>
          {[-1, 1].map((l) =>
            [0.22, 0.02, -0.18].map((y) => (
              <Peca key={`${l}${y}`} cor="#2a2a30" pos={[l * 0.17, y, 0.29]}>
                <sphereGeometry args={[0.022, 10, 8]} />
              </Peca>
            )),
          )}
          {/* gola e barra listradas */}
          {listras.map((cor, i) => (
            <Peca key={`g${i}`} cor={cor} pos={[0, 0.4 + i * 0.018, 0.0]} rot={[Math.PI / 2, 0, 0]} fosco>
              <torusGeometry args={[0.22 - i * 0.004, 0.035, 10, 32]} />
            </Peca>
          ))}
          {listras.map((cor, i) => (
            <Peca key={`b${i}`} cor={cor} pos={[0, -0.5 + i * 0.024, 0]} esc={[1, 1, 0.78]} fosco>
              <cylinderGeometry args={[0.37, 0.37, 0.026, 32]} />
            </Peca>
          ))}
          {/* patches: amarelo no peito esquerdo, preto no direito, letreiro vermelho embaixo */}
          <Peca cor="#e9b949" pos={[-0.2, 0.14, 0.27]} rot={[0, -0.35, 0]}>
            <boxGeometry args={[0.13, 0.13, 0.02]} />
          </Peca>
          <Peca cor="#151518" pos={[0.21, 0.16, 0.26]} rot={[0, 0.4, 0]}>
            <boxGeometry args={[0.12, 0.08, 0.02]} />
          </Peca>
          <Peca cor="#b8322a" pos={[0.2, -0.17, 0.26]} rot={[0, 0.4, 0.3]} esc={[1, 0.7, 0.2]}>
            <sphereGeometry args={[0.075, 16, 12]} />
          </Peca>
        </>
      ) : null}
      {acessorios.bolsa ? (
        <>
          {/* alça transversal do ombro direito ao quadril esquerdo, e a bolsinha */}
          <Peca cor="#1b1b1f" pos={[0.02, 0.0, 0.29]} rot={[0, 0, -0.62]}>
            <boxGeometry args={[0.035, 0.98, 0.02]} />
          </Peca>
          <Peca cor="#8a7358" pos={[-0.33, -0.42, 0.2]} rot={[0, -0.4, 0]}>
            <boxGeometry args={[0.16, 0.22, 0.07]} />
          </Peca>
        </>
      ) : null}
      {roupa === 'jaqueta' ? (
        <>
          {/* camiseta aparecendo no meio da jaqueta aberta */}
          <Peca cor={c.baixo} pos={[0, 0.02, 0.27]} esc={[1, 1, 0.4]}>
            <boxGeometry args={[0.2, 0.7, 0.1]} />
          </Peca>
          {/* gola */}
          <Peca cor={c.roupa} pos={[0, 0.42, 0.02]} rot={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[0.2, 0.06, 12, 28]} />
          </Peca>
        </>
      ) : null}
    </group>
  );

  const fios = useMemo(
    () =>
      // dois anéis de cachos e um miolo alto: volume em cima, lados mais baixos
      [
        ...Array.from({length: 30}, (_, i) => {
          const a = (i / 30) * Math.PI * 2;
          return {x: Math.cos(a) * 0.86, z: Math.sin(a) * 0.86, y: 0.28 + ((i * 7) % 3) * 0.05, r: 0.17 + ((i * 5) % 4) * 0.015};
        }),
        ...Array.from({length: 20}, (_, i) => {
          const a = (i / 20) * Math.PI * 2 + 0.3;
          return {x: Math.cos(a) * 0.56, z: Math.sin(a) * 0.56 + 0.06, y: 0.62 + ((i * 3) % 3) * 0.05, r: 0.2 + ((i * 7) % 3) * 0.02};
        }),
        // miolo do topo: cachos menores e baixos, só para cobrir o couro de quem olha de cima
        ...Array.from({length: 7}, (_, i) => ({x: i ? Math.cos(i) * 0.24 : 0, z: i ? Math.sin(i) * 0.24 : 0, y: 0.62, r: 0.2})),
        // cachinhos na linha do cabelo, para não ficar uma borda reta de capacete
        ...Array.from({length: 24}, (_, i) => {
          const a = (i / 24) * Math.PI * 2;
          return {x: Math.cos(a) * 0.95, z: Math.sin(a) * 0.95, y: 0.06 + ((i * 5) % 3) * 0.04, r: 0.13 + ((i * 3) % 3) * 0.015};
        }),
        // cachinhos caindo na testa
        ...[-0.42, -0.16, 0.12, 0.38].map((x, i) => ({x, z: 0.84, y: 0.44 - (i % 2) * 0.06, r: 0.14})),
      ],
    [],
  );

  // mullet: os mesmos cachos jogados para trás, mais um tufo na nuca até abaixo da orelha
  const recuo = cabelo === 'mullet' ? 0.14 : 0;
  const nuca = useMemo(
    () =>
      cabelo !== 'mullet'
        ? []
        : Array.from({length: 60}, (_, i) => {
            // cachos colados na superfície da cabeça, só na parte de trás (de orelha a orelha),
            // em cinco fileiras que descem do topo até a nuca
            const fileira = Math.floor(i / 12);
            // em cima pode ir até acima da orelha; embaixo fica só atrás (lados curtos do mullet)
            const abre = fileira < 2 ? 1.7 : 1.05;
            const az = (-1 + (2 * (i % 12)) / 11) * abre + (fileira % 2) * 0.08; // ângulo em volta da nuca
            const el = 0.35 - fileira * 0.3; // altura: de cima até abaixo da orelha
            const d = 1.04;
            return {
              x: Math.sin(az) * Math.cos(el) * d,
              y: Math.sin(el) * d,
              z: -Math.cos(az) * Math.cos(el) * d,
              r: 0.2 - fileira * 0.012 + ((i * 5) % 3) * 0.012,
            };
          }).concat(
            // mais 4 cachos de cada lado, abaixo da orelha, que aparecem de frente
            [-1, 1].flatMap((lado) =>
              [
                [1.25, -0.35],
                [1.42, -0.5],
                [1.3, -0.68],
                [1.5, -0.82],
              ].map(([az, el], k) => ({
                x: lado * Math.sin(az) * Math.cos(el) * 1.04,
                y: Math.sin(el) * 1.04,
                z: -Math.cos(az) * Math.cos(el) * 1.04,
                r: 0.17 + (k % 2) * 0.02,
              })),
            ),
          ),
    [cabelo],
  );

  const cabeloForma =
    cabelo === 'tigela' ? (
      <>
        <Peca cor={c.cabelo} pos={[0, R * 0.18, -R * 0.06]} esc={[1.06, 0.9, 1.04]}>
          <sphereGeometry args={[R, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.46]} />
        </Peca>
      </>
    ) : cabelo === 'topete' ? (
      <>
        {/* lados curtos e topete levantado na frente */}
        <Peca cor={c.cabelo} pos={[0, R * 0.12, -R * 0.08]} esc={[1.04, 0.95, 1.03]}>
          <sphereGeometry args={[R, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.42]} />
        </Peca>
        <Peca cor={c.cabelo} pos={[R * 0.08, R * 0.92, R * 0.36]} rot={[-0.5, 0, -0.25]} esc={[1.25, 0.75, 1]}>
          <sphereGeometry args={[R * 0.42, 28, 20]} />
        </Peca>
        <Peca cor={c.cabelo} pos={[-R * 0.3, R * 0.86, R * 0.22]} rot={[-0.3, 0, 0.3]} esc={[1, 0.7, 1]}>
          <sphereGeometry args={[R * 0.34, 24, 16]} />
        </Peca>
      </>
    ) : (
      <>
        {/* cachos: bolinhas em volta do topo */}
        <Peca cor={c.cabelo} pos={[0, R * 0.2, -R * 0.05]} esc={[1.05, 0.9, 1.04]}>
          <sphereGeometry args={[R, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.44]} />
        </Peca>
        {fios.map((f, i) => (
          <Peca key={i} cor={c.cabelo} pos={[f.x * R, f.y * R + R * 0.32, (f.z - recuo) * R]} fosco>
            <sphereGeometry args={[f.r * R, 16, 12]} />
          </Peca>
        ))}
        {nuca.map((f, i) => (
          <Peca key={`n${i}`} cor={c.cabelo} pos={[f.x * R, f.y * R, f.z * R]} fosco>
            <sphereGeometry args={[f.r * R, 16, 12]} />
          </Peca>
        ))}
      </>
    );

  const acabamento = useMemo(() => ({estilo, degraus}), [estilo, degraus]);
  return (
    <Acabamento.Provider value={acabamento}>
    <group position={position} rotation={rotation} scale={escala}>
      {perna(-1, pose.pernaE, pose.joelhoE)}
      {perna(1, pose.pernaD, pose.joelhoD)}
      {/* do quadril para cima: inclina junto (girando no quadril) */}
      <group position={[0, 0.86, 0]} rotation={[pose.inclina ?? 0, 0, 0]}>
      <group position={[0, -0.86, 0]}>
      {tronco}
      {braco(-1, pose.bracoE, pose.cotoveloE)}
      {braco(1, pose.bracoD, pose.cotoveloD, naMao)}
      {/* pescoço */}
      <Peca cor={c.pele} pos={[0, 1.78, 0]}>
        <cylinderGeometry args={[0.13, 0.15, 0.14, 20]} />
      </Peca>
      {acessorios.tatuagem
        ? [
            [0.07, 1.8, 0.11],
            [-0.05, 1.76, 0.12],
            [0.1, 1.74, 0.07],
          ].map((p, i) => (
            // tatuagem do pescoço: manchinhas escuras coladas na pele
            <mesh key={i} position={p as V} scale={[1, 0.8, 0.25]}>
              <sphereGeometry args={[0.035 + i * 0.008, 12, 10]} />
              <meshStandardMaterial color="#3b3d4a" roughness={0.7} />
            </mesh>
          ))
        : null}
      <group position={[0, 1.8 + R, 0]} rotation={[cabX, cabY, 0]}>
        <Peca cor={c.pele} esc={estilo === 'massinha' ? [1, 0.94, 0.92] : [1, 1, 0.95]}>
          <sphereGeometry args={[R, 40, 32]} />
        </Peca>
        {cabeloForma}
        {/* orelhas */}
        {[-1, 1].map((l) => (
          <Peca key={l} cor={c.pele} pos={[l * R * 0.98, -R * 0.05, 0]} esc={[0.5, 1, 0.8]}>
            <sphereGeometry args={[R * 0.18, 16, 12]} />
          </Peca>
        ))}
        {/* olhos com brilho */}
        {[-1, 1].map((l) => (
          <group key={l} position={[l * R * 0.34, R * 0.0, R * (rostoNovo ? 0.84 : 0.9)]} scale={[rosto.olhoEsc, rosto.olhoEsc * rosto.olhoY, rosto.olhoEsc * (rostoNovo ? 0.5 : 1)]}>
            <mesh>
              <sphereGeometry args={[rostoNovo ? R * 0.14 : estilo === 'vinil' ? R * 0.15 : R * 0.1, 20, 16]} />
              <meshStandardMaterial color="#141414" roughness={0.2} />
            </mesh>
            {estilo !== 'massinha' || rostoNovo ? (
              <mesh position={[R * 0.04, R * 0.05, R * (rostoNovo ? 0.13 : estilo === 'vinil' ? 0.12 : 0.08)]}>
                <sphereGeometry args={[R * 0.04, 12, 10]} />
                <meshBasicMaterial color="#ffffff" />
              </mesh>
            ) : null}
          </group>
        ))}
        {/* sobrancelhas */}
        {[-1, 1].map((l) => (
          // cápsula deitada (gira 90° no próprio lugar) e levemente inclinada
          <mesh key={l} position={[l * R * 0.34, R * (0.27 + rosto.sobY), R * (rostoNovo ? 0.83 : 0.88)]} rotation={[0, 0, Math.PI / 2 + l * rosto.sobGiro]}>
            <capsuleGeometry args={[R * 0.03, R * 0.16, 6, 10]} />
            <meshStandardMaterial color={c.cabelo} roughness={0.6} />
          </mesh>
        ))}
        {/* bochechas */}
        {[-1, 1].map((l) => (
          <mesh key={l} position={[l * R * 0.55, -R * 0.22, R * 0.78]} scale={[1, 0.6, 0.4]}>
            <sphereGeometry args={[R * 0.13, 16, 12]} />
            <meshStandardMaterial color="#f28a8a" roughness={0.9} transparent opacity={0.7} />
          </mesh>
        ))}
        {estilo === 'massinha' ? (
          <Peca cor={c.pele} pos={[0, -R * 0.12, R * 0.96]}>
            <sphereGeometry args={[R * 0.11, 16, 12]} />
          </Peca>
        ) : null}
        {barba === 'cavanhaque' ? (
          <>
            {/* cavanhaque embaixo da boca */}
            <Peca cor={c.cabelo} pos={[0, -R * 0.68, R * 0.66]} esc={[0.75, 1.1, 0.5]} fosco>
              <sphereGeometry args={[R * 0.13, 20, 14]} />
            </Peca>
          </>
        ) : null}
        {acessorios.brinco ? (
          <mesh position={[-R * 0.99, -R * 0.24, R * 0.05]}>
            <sphereGeometry args={[R * 0.05, 12, 10]} />
            <meshStandardMaterial color="#e8e8ea" metalness={1} roughness={0.15} />
          </mesh>
        ) : null}
        {/* boca: muda com a expressão */}
        {fala > 0.08 ? (
          <mesh position={[0, -R * 0.4, R * 0.88]} scale={[1.05, 0.35 + 0.95 * fala, 0.4]}>
            <sphereGeometry args={[R * 0.13, 16, 12]} />
            <meshStandardMaterial color="#3a1f18" roughness={0.6} />
          </mesh>
        ) : rosto.boca === 'sorriso' || rosto.boca === 'sorrisao' ? (
          <mesh position={[0, -R * 0.34, R * 0.86]} rotation={[0.35, 0, Math.PI]}>
            <torusGeometry args={[R * (rosto.boca === 'sorrisao' ? 0.21 : 0.16), R * 0.03, 8, 24, Math.PI]} />
            <meshStandardMaterial color="#3a1f18" roughness={0.6} />
          </mesh>
        ) : rosto.boca === 'triste' ? (
          <mesh position={[0, -R * 0.5, R * 0.86]} rotation={[0.45, 0, 0]}>
            <torusGeometry args={[R * 0.14, R * 0.03, 8, 24, Math.PI]} />
            <meshStandardMaterial color="#3a1f18" roughness={0.6} />
          </mesh>
        ) : rosto.boca === 'o' ? (
          <mesh position={[0, -R * 0.4, R * 0.88]} scale={[0.8, 1, 0.4]}>
            <sphereGeometry args={[R * 0.12, 16, 12]} />
            <meshStandardMaterial color="#3a1f18" roughness={0.6} />
          </mesh>
        ) : (
          <mesh position={[0, -R * 0.38, R * 0.9]} rotation={[0, 0, Math.PI / 2]}>
            <capsuleGeometry args={[R * 0.025, R * 0.18, 6, 10]} />
            <meshStandardMaterial color="#3a1f18" roughness={0.6} />
          </mesh>
        )}
        {/* suor: gotas que nascem na testa e escorrem pela lateral do rosto */}
        {suor > 0
          ? [
              [-0.8, 0.42, 0.0],
              [0.82, 0.38, 0.37],
              [-0.7, 0.55, 0.71],
            ].map(([x, y, fase], i) => {
              // nascem nas têmporas e descem pela lateral do rosto, longe dos olhos
              const ciclo = (tempo * 0.7 + fase) % 1;
              const yy = y - ciclo * 0.55;
              const zz = Math.sqrt(Math.max(0.05, 1 - x * x - yy * yy)) * 1.01;
              return (
                <mesh key={i} position={[x * R, yy * R, zz * R]} scale={[0.75, 1.15, 0.75]}>
                  <sphereGeometry args={[R * 0.07 * suor * (1 - ciclo * 0.3), 14, 10]} />
                  <meshPhysicalMaterial color="#8fd0ff" roughness={0.05} clearcoat={1} transparent opacity={0.9 * (1 - ciclo * 0.6)} />
                </mesh>
              );
            })
          : null}
      </group>
      </group>
      </group>
    </group>
    </Acabamento.Provider>
  );
};
