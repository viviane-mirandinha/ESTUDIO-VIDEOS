// Kit cotidiano.explicado · de cotidiano.explicado (@cotidiano.explicado) · não pode ser revendido nem usado para criar um produto parecido (LICENCA.md).
import React, {useEffect, useMemo} from 'react';
import * as THREE from 'three';

/**
 * O gato do kit, montado com formas simples. Olha para +z, com as patas no chão (y = 0)
 * e uns 1,1 de comprimento. A pose é só ângulos: anime mudando-os a partir do segundo atual.
 */

type V = [number, number, number];

export type ExpressaoGato = 'neutro' | 'curioso' | 'alerta' | 'feliz' | 'surpreso' | 'incomodado' | 'sereno';

export type PoseGato = {
  /** Corpo inteiro inclina para frente (radianos, + = focinho para baixo). */
  corpo?: number;
  /** 0 → 1: abaixa o corpo (cavando, espreitando). */
  agacha?: number;
  /** 0 → 1: senta com o peito erguido. */
  senta?: number;
  /** Cabeça: [inclina para baixo, vira para os lados]. */
  cabeca?: [number, number];
  /** Patas da frente e de trás (radianos, + = para frente). */
  pataDE?: number;
  pataDD?: number;
  pataTE?: number;
  pataTD?: number;
  /** Rabo: [balanço para os lados, quanto sobe 0 → 1]. */
  rabo?: [number, number];
  /** Orelhas: -1 coladas para trás, 0 normais, 1 em pé. */
  orelhas?: number;
};

const ROSTO: Record<ExpressaoGato, {olhoY: number; olhoEsc: number; pupila: number; boca: 'sorriso' | 'reta' | 'o' | 'triste'; orelhas: number}> = {
  neutro: {olhoY: 1, olhoEsc: 1, pupila: 0.55, boca: 'sorriso', orelhas: 0.1},
  curioso: {olhoY: 1.05, olhoEsc: 1.12, pupila: 0.85, boca: 'sorriso', orelhas: 0.8},
  alerta: {olhoY: 1.1, olhoEsc: 1.12, pupila: 0.28, boca: 'reta', orelhas: 1},
  feliz: {olhoY: 0.5, olhoEsc: 1.05, pupila: 0.7, boca: 'sorriso', orelhas: 0.3},
  surpreso: {olhoY: 1.25, olhoEsc: 1.25, pupila: 0.95, boca: 'o', orelhas: 1},
  incomodado: {olhoY: 0.4, olhoEsc: 1, pupila: 0.4, boca: 'triste', orelhas: -0.6},
  sereno: {olhoY: 0.55, olhoEsc: 1, pupila: 0.6, boca: 'sorriso', orelhas: 0},
};

export type CoresGato = {pelo: string; listra: string; branco: string; olho: string; nariz: string; coleira: string};

export const GATO_LARANJA: CoresGato = {pelo: '#f08a2c', listra: '#c4601a', branco: '#fff2e2', olho: '#6fd04c', nariz: '#f29aa0', coleira: '#d93a2b'};
export const GATO_CINZA: CoresGato = {pelo: '#8d949c', listra: '#656c75', branco: '#e9edf0', olho: '#e8c34a', nariz: '#e8a0a8', coleira: '#3f7fd0'};

/** Uma peça de pelo: macia, com um brilho suave nas bordas. */
const Malha: React.FC<{cor: string; pos?: V; rot?: V; esc?: V; sombra?: boolean; liso?: boolean; children: React.ReactElement}> = ({cor, pos, rot, esc, sombra = true, liso, children}) => (
  <mesh position={pos} rotation={rot} scale={esc} castShadow={sombra} receiveShadow>
    {children}
    <meshPhysicalMaterial color={cor} roughness={liso ? 0.45 : 0.9} sheen={liso ? 0 : 0.8} sheenRoughness={0.45} sheenColor="#fff0dc" />
  </mesh>
);

const PI = Math.PI;

export const Gato: React.FC<{
  cores?: Partial<CoresGato>;
  pose?: PoseGato;
  expressao?: ExpressaoGato;
  /** Quanto o olho está aberto (1 aberto → 0 fechado), para piscar. */
  piscar?: number;
  coleira?: boolean;
  listras?: boolean;
  /** Cabeça maior e patas curtas. */
  filhote?: boolean;
  /** 0 → 1: a língua rosa para fora (lambendo). */
  lingua?: number;
  /** Quanto um dos olhos está aberto, se for diferente do outro (abre um olho só). */
  piscarUm?: number;
  position?: V;
  rotation?: V;
  escala?: number;
}> = ({cores, pose = {}, expressao = 'neutro', piscar = 1, coleira = false, listras = true, filhote = false, lingua = 0, piscarUm, position, rotation, escala = 1}) => {
  const c = {...GATO_LARANJA, ...cores};
  const r = ROSTO[expressao];
  const agacha = pose.agacha ?? 0;
  const senta = pose.senta ?? 0;
  const tronco = (pose.corpo ?? 0) - 0.7 * senta;
  const [cabP, cabY] = pose.cabeca ?? [0, 0];
  const orelhas = pose.orelhas ?? r.orelhas;
  const [balanco, sobe] = pose.rabo ?? [0, 0.3];
  const olhoY = Math.max(0.06, r.olhoY * piscar);
  const baixa = 0.2 * agacha + 0.22 * senta;
  const hCab = filhote ? 1.28 : 1;

  const pata = (lado: 1 | -1, ang: number, frente: boolean) => {
    const topo = frente ? 0.34 - baixa + 0.1 * Math.cos(tronco) - 0.7 * Math.sin(tronco) : 0.4 - baixa;
    const k = Math.max(0.2, topo / (frente ? 0.44 : 0.4));
    return (
      <group position={[0.17 * lado, frente ? -0.08 : 0, frente ? 0.32 : 0]} rotation={[-ang - (frente ? tronco : 0), 0, lado * 0.04]}>
        <group scale={[1, k, 1]}>
          <Malha cor={c.pelo} pos={[0, -0.17, 0]}>
            <capsuleGeometry args={[0.075, 0.2, 8, 14]} />
          </Malha>
          <Malha cor={c.branco} pos={[0, -0.36, 0.03]} esc={[1, 0.72, 1.3]}>
            <sphereGeometry args={[0.1, 18, 14]} />
          </Malha>
        </group>
      </group>
    );
  };

  const tubo = useMemo(() => {
    const pts: THREE.Vector3[] = [new THREE.Vector3(0, 0, 0)];
    let x = 0;
    let y = 0;
    let z = 0;
    for (let i = 0; i < 5; i++) {
      const teta = -1.1 + sobe * 0.9 + 0.3 * i;
      const giro = balanco * (0.4 + i * 0.18);
      const dy = Math.cos(teta) * 0.2;
      const dz = Math.sin(teta) * 0.2;
      x += Math.sin(giro) * Math.abs(dz);
      y += dy;
      z += dz * Math.cos(giro);
      pts.push(new THREE.Vector3(x, y, z));
    }
    return {geo: new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 28, 0.056, 12, false), ponta: pts[pts.length - 1]};
  }, [balanco, sobe]);
  useEffect(() => () => tubo.geo.dispose(), [tubo]);

  const orelha = (lado: 1 | -1) => {
    const baixo = Math.max(0, -orelhas);
    const alto = Math.max(0, orelhas);
    return (
      <group position={[0.18 * lado, 0.24, -0.02]} rotation={[0.5 * baixo - 0.12 * alto, 0, -lado * (0.3 + 0.55 * baixo)]}>
        <Malha cor={c.pelo} pos={[0, 0.09, 0]} esc={[1, 1, 0.55]}>
          <coneGeometry args={[0.115, 0.23, 14]} />
        </Malha>
        <Malha cor={c.nariz} pos={[0, 0.075, 0.035]} esc={[1, 1, 0.4]} sombra={false} liso>
          <coneGeometry args={[0.07, 0.15, 14]} />
        </Malha>
      </group>
    );
  };

  const olho = (lado: 1 | -1) => (
    <group position={[0.125 * lado, 0.045, 0.262]} scale={[r.olhoEsc, r.olhoEsc * (lado === -1 && piscarUm !== undefined ? Math.max(0.06, r.olhoY * piscarUm) : olhoY), r.olhoEsc * 0.6]}>
      <mesh>
        <sphereGeometry args={[0.066, 22, 16]} />
        <meshStandardMaterial color={c.olho} roughness={0.25} />
      </mesh>
      <mesh position={[0, 0, 0.066]} scale={[r.pupila, 1, 0.5]}>
        <sphereGeometry args={[0.047, 18, 14]} />
        <meshStandardMaterial color="#141414" roughness={0.2} />
      </mesh>
      <mesh position={[0.024 * lado, 0.028, 0.082]}>
        <sphereGeometry args={[0.019, 10, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
    </group>
  );

  const boca = () => {
    const arco = (x: number, rot: number) => (
      <mesh key={x} position={[x, -0.112, 0.323]} rotation={[0, 0, rot]}>
        <torusGeometry args={[0.03, 0.0065, 6, 16, PI]} />
        <meshStandardMaterial color="#5a2a20" roughness={0.6} />
      </mesh>
    );
    if (r.boca === 'o')
      return (
        <mesh position={[0, -0.125, 0.318]} scale={[0.8, 1, 0.5]}>
          <sphereGeometry args={[0.026, 12, 10]} />
          <meshStandardMaterial color="#4a1f18" roughness={0.6} />
        </mesh>
      );
    if (r.boca === 'triste') return [arco(-0.03, 0), arco(0.03, 0)];
    if (r.boca === 'reta')
      return (
        <mesh position={[0, -0.118, 0.322]} rotation={[0, 0, PI / 2]}>
          <capsuleGeometry args={[0.005, 0.07, 4, 8]} />
          <meshStandardMaterial color="#5a2a20" roughness={0.6} />
        </mesh>
      );
    return [arco(-0.03, PI), arco(0.03, PI)];
  };

  const mexe = {sombra: false};
  return (
    <group position={position} rotation={rotation} scale={escala * (filhote ? 0.55 : 1)}>
      {/* patas de trás e rabo ficam onde o corpo senta */}
      {[-1, 1].map((l) => (
        <group key={l} position={[0.2 * l, 0.4 - baixa, -0.3]}>
          <Malha cor={c.pelo} pos={[0, 0.02, 0]} esc={[0.8, 1, 1.05]}>
            <sphereGeometry args={[0.2, 24, 18]} />
          </Malha>
          <group rotation={[-(l === -1 ? (pose.pataTE ?? 0) : (pose.pataTD ?? 0)) + 1.45 * senta, 0, 0]}>
            <group scale={[1, (0.4 - baixa) / 0.4, 1]}>
              <Malha cor={c.pelo} pos={[0, -0.17, 0]}>
                <capsuleGeometry args={[0.07, 0.17, 8, 14]} />
              </Malha>
              <Malha cor={c.branco} pos={[0, -0.36, 0.04]} esc={[1, 0.72, 1.35]}>
                <sphereGeometry args={[0.1, 18, 14]} />
              </Malha>
            </group>
          </group>
        </group>
      ))}
      <group position={[0, 0.46 - baixa, -0.45]}>
        <mesh geometry={tubo.geo} castShadow receiveShadow>
          <meshPhysicalMaterial color={c.pelo} roughness={0.9} sheen={0.8} sheenRoughness={0.45} sheenColor="#fff0dc" />
        </mesh>
        <mesh position={tubo.ponta} castShadow>
          <sphereGeometry args={[0.057, 14, 12]} />
          <meshPhysicalMaterial color={listras ? c.listra : c.pelo} roughness={0.9} />
        </mesh>
      </group>

      {/* do quadril para a frente: inclina junto (agachar, sentar) */}
      <group position={[0, 0.34 - baixa, -0.38]} rotation={[tronco + 0, 0, 0]}>
        <group position={[0, 0.18, 0.38]}>
          <Malha cor={c.pelo} esc={[0.62, 0.56, 1]}>
            <sphereGeometry args={[0.5, 40, 28]} />
          </Malha>
          {listras
            ? [-0.3, -0.12, 0.06, 0.24].map((z) => {
                const k = Math.sqrt(1 - (z / 0.5) ** 2);
                return (
                  <mesh key={z} position={[0, 0, z]} scale={[1, 0.93, 1]} {...mexe}>
                    <torusGeometry args={[0.31 * k - 0.002, 0.019, 8, 28, PI]} />
                    <meshStandardMaterial color={c.listra} roughness={0.9} />
                  </mesh>
                );
              })
            : null}
          <Malha cor={c.branco} pos={[0, -0.06, 0.36]} esc={[0.85, 1, 0.75]}>
            <sphereGeometry args={[0.22, 22, 16]} />
          </Malha>
          {pata(-1, pose.pataDE ?? 0, true)}
          {pata(1, pose.pataDD ?? 0, true)}
          {coleira ? (
            <group position={[0, 0.04, 0.4]} rotation={[-0.93, 0, 0]}>
              <mesh>
                <torusGeometry args={[0.215, 0.032, 10, 36]} />
                <meshStandardMaterial color={c.coleira} roughness={0.5} />
              </mesh>
              <mesh position={[0, -0.215, 0.03]}>
                <sphereGeometry args={[0.042, 14, 12]} />
                <meshStandardMaterial color="#f4c542" roughness={0.25} metalness={0.8} />
              </mesh>
            </group>
          ) : null}

          {/* cabeça */}
          <group position={[0, 0.14, 0.42]} rotation={[cabP - tronco * 0.7, cabY, 0]}>
            <group position={[0, 0.13, 0.17]} scale={hCab}>
              <Malha cor={c.pelo} esc={[1.12, 0.95, 1]}>
                <sphereGeometry args={[0.3, 36, 28]} />
              </Malha>
              {listras
                ? [-0.075, 0, 0.075].map((x) => (
                    <mesh key={x} position={[x, 0.282, 0.09]} rotation={[PI / 2 - 0.15, 0, x * 3]} {...mexe}>
                      <capsuleGeometry args={[0.012, 0.1, 4, 8]} />
                      <meshStandardMaterial color={c.listra} roughness={0.9} />
                    </mesh>
                  ))
                : null}
              {orelha(-1)}
              {orelha(1)}
              {[-1, 1].map((l) => (
                <React.Fragment key={l}>
                  {olho(l as 1 | -1)}
                  <Malha cor={c.branco} pos={[0.055 * l, -0.085, 0.245]} sombra={false}>
                    <sphereGeometry args={[0.075, 18, 14]} />
                  </Malha>
                  {[0, 1, 2].map((j) => (
                    <mesh key={j} position={[0.2 * l, -0.07 + j * 0.032, 0.25]} rotation={[0, -l * 0.35, PI / 2 + l * (j - 1) * 0.2]}>
                      <cylinderGeometry args={[0.0035, 0.0035, 0.2, 5]} />
                      <meshBasicMaterial color="#ffffff" />
                    </mesh>
                  ))}
                </React.Fragment>
              ))}
              <mesh position={[0, -0.035, 0.298]} scale={[1, 0.7, 0.7]}>
                <sphereGeometry args={[0.032, 12, 10]} />
                <meshStandardMaterial color={c.nariz} roughness={0.4} />
              </mesh>
              {boca()}
              {lingua > 0.02 ? (
                <mesh position={[0, -0.138 - 0.02 * lingua, 0.318 + 0.05 * lingua]} rotation={[0.5, 0, 0]} scale={[0.048, 0.016, 0.02 + 0.1 * lingua]}>
                  <sphereGeometry args={[1, 16, 12]} />
                  <meshStandardMaterial color="#f08a8a" roughness={0.35} />
                </mesh>
              ) : null}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};
