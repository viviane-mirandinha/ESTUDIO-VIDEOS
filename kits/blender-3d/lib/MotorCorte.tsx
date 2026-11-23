import React from 'react';
import * as THREE from 'three';
import {Fogo} from './Objetos';

/**
 * Motor de carro em CORTE (visto de lado): cilindro aberto, pistão, biela, virabrequim, volante,
 * correia, alternador, bateria, vela. Tudo é guiado por números (sem estado):
 *  - `ang`      ângulo do virabrequim em radianos (0 = pistão no ponto mais alto; sentido horário)
 *  - `mistura`  0 → 1  câmara cheia de ar + combustível
 *  - `entrada`  0 → 1  progresso das bolinhas de ar/combustível entrando (0 = não aparecem)
 *  - `faisca`   0 → 1  brilho da faísca da vela
 *  - `chama`    0 → 1  explosão na câmara
 *  - `carga`    0 → 1  bateria enchendo (e alternador brilhando)
 *  - `foco`     peça destacada em amarelo: 'pistao' | 'volante' | 'correia' | 'alternador' | 'bateria' | 'vela'
 *  - `tempo`    segundo atual (só para tremular o destaque e a chama)
 * Origem = centro do virabrequim; o cilindro sobe em +y; o corte olha para +z.
 * Cada forma que muda é um <mesh> próprio.
 */
export type FocoMotor = 'pistao' | 'volante' | 'correia' | 'alternador' | 'bateria' | 'vela' | '';

const R = 0.35; // raio da manivela
const L = 1.1; // comprimento da biela
const PISTAO_ALTURA = 0.45;
const TETO = 1.85; // teto da câmara de combustão
const VOLANTE_R = 0.55;
const ALT_R = 0.2;
export const MOTOR_ALTERNADOR: [number, number] = [-1.5, -1.1];
export const MOTOR_BATERIA: [number, number] = [-1.5, -2.7];
const Z_CORREIA = 0.5;

type V2 = [number, number];

/** Caixa fina ligando dois pontos do plano (x,y), em um z dado. */
const Barra: React.FC<{a: V2; b: V2; z: number; esp: number; prof: number; cor: string; emissivo?: string; forca?: number; rugo?: number; metal?: number}> = ({a, b, z, esp, prof, cor, emissivo = '#000000', forca = 0, rugo = 0.5, metal = 0.2}) => {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const comp = Math.hypot(dx, dy);
  return (
    <mesh position={[(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z]} rotation={[0, 0, -Math.atan2(dx, dy)]} castShadow>
      <boxGeometry args={[esp, comp, prof]} />
      <meshStandardMaterial color={cor} roughness={rugo} metalness={metal} emissive={emissivo} emissiveIntensity={forca} />
    </mesh>
  );
};

export const MotorCorte: React.FC<{
  ang?: number;
  mistura?: number;
  entrada?: number;
  faisca?: number;
  chama?: number;
  carga?: number;
  foco?: FocoMotor;
  tempo?: number;
}> = ({ang = 0, mistura = 0, entrada = 0, faisca = 0, chama = 0, carga = 0, foco = '', tempo = 0}) => {
  const pisca = 0.55 + 0.35 * Math.sin(tempo * 9);
  const dest = (nome: FocoMotor) => ({emissive: foco === nome ? '#ffc61a' : '#000000', emissiveIntensity: foco === nome ? pisca : 0});

  // posições (o virabrequim gira no sentido horário: ângulo z negativo)
  const pino: V2 = [R * Math.sin(ang), R * Math.cos(ang)];
  const py = R * Math.cos(ang) + Math.sqrt(L * L - R * R * Math.sin(ang) * Math.sin(ang));
  const topo = py + PISTAO_ALTURA / 2;
  const altCamara = Math.max(0.05, TETO - topo);

  // correia: tangente externa entre o volante e a polia do alternador
  const [ax, ay] = MOTOR_ALTERNADOR;
  const D = Math.hypot(ax, ay);
  const u: V2 = [ax / D, ay / D];
  const perp: V2 = [-u[1], u[0]];
  const sb = (VOLANTE_R - ALT_R) / D;
  const cb = Math.sqrt(1 - sb * sb);
  const lados = [1, -1].map((sg) => {
    const n: V2 = [u[0] * sb + sg * perp[0] * cb, u[1] * sb + sg * perp[1] * cb];
    const p1: V2 = [VOLANTE_R * n[0], VOLANTE_R * n[1]];
    const p2: V2 = [ax + ALT_R * n[0], ay + ALT_R * n[1]];
    const t: V2 = [p2[0] - p1[0], p2[1] - p1[1]];
    const comp = Math.hypot(t[0], t[1]);
    const dir = n[1] * t[0] - n[0] * t[1] >= 0 ? 1 : -1; // sentido do aro (horário) ao longo da correia
    return {p1, p2, comp, dir};
  });
  const NERV = 6;
  const passoNerv = 0.3;
  const fase = (-ang * VOLANTE_R) / passoNerv;
  const correiaCor = '#17181c';

  // bolinhas de ar (azul) e combustível (amarelo) descendo pelo tubo de entrada
  const caminho = (k: number): [number, number] => {
    // tubo horizontal em y = 2.6 de x = -1.7 até x = -0.3, depois desce até a câmara
    const tot = 1.4 + 1.2;
    const d = k * tot;
    return d < 1.4 ? [-1.7 + d, 2.6] : [-0.3, 2.6 - (d - 1.4)];
  };

  const corMistura = new THREE.Color('#222833').lerp(new THREE.Color('#b9d97a'), Math.min(1, Math.max(0, mistura)));
  const corFogo = corMistura.clone().lerp(new THREE.Color('#ff7a1a'), Math.min(1, Math.max(0, chama)));

  return (
    <group>
      {/* placa do fundo do bloco */}
      <mesh position={[0, 0.7, -0.55]} receiveShadow>
        <boxGeometry args={[1.7, 3.5, 0.1]} />
        <meshStandardMaterial color="#3a404c" roughness={0.6} metalness={0.3} />
      </mesh>
      {/* metade de trás do cilindro (corte aberto) */}
      <mesh position={[0, 1.2, 0]} castShadow>
        <cylinderGeometry args={[0.44, 0.44, 1.35, 40, 1, true, Math.PI / 2, Math.PI]} />
        <meshStandardMaterial color="#aab2c0" roughness={0.35} metalness={0.6} side={THREE.DoubleSide} />
      </mesh>
      {/* cabeçote */}
      <mesh position={[0, 2.08, 0]} castShadow>
        <boxGeometry args={[1.2, 0.45, 0.9]} />
        <meshStandardMaterial color="#6d7686" roughness={0.45} metalness={0.5} />
      </mesh>
      {/* tubo de entrada */}
      <mesh position={[-1.0, 2.6, 0]} castShadow>
        <boxGeometry args={[1.5, 0.22, 0.3]} />
        <meshStandardMaterial color="#4a5160" roughness={0.5} metalness={0.4} />
      </mesh>
      <mesh position={[-0.3, 2.45, 0]} castShadow>
        <boxGeometry args={[0.22, 0.4, 0.3]} />
        <meshStandardMaterial color="#4a5160" roughness={0.5} metalness={0.4} />
      </mesh>
      {/* vela */}
      <mesh position={[0, 2.62, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.09, 0.5, 16]} />
        <meshStandardMaterial color="#e8e2d0" roughness={0.3} {...dest('vela')} />
      </mesh>
      <mesh position={[0, 2.38, 0]}>
        <cylinderGeometry args={[0.13, 0.13, 0.1, 6]} />
        <meshStandardMaterial color="#8d95a3" roughness={0.4} metalness={0.7} />
      </mesh>
      <mesh position={[0, TETO - 0.06, 0]}>
        <cylinderGeometry args={[0.03, 0.03, 0.14, 8]} />
        <meshStandardMaterial color="#c9ced8" roughness={0.3} metalness={0.8} />
      </mesh>
      {faisca > 0.02 ? (
        <group position={[0, TETO - 0.18, 0.05]}>
          <mesh>
            <sphereGeometry args={[0.07 + 0.12 * faisca, 14, 10]} />
            <meshStandardMaterial color="#fff6c8" emissive="#fff0a0" emissiveIntensity={2.5 * faisca} />
          </mesh>
          {[0, 1, 2, 3, 4, 5].map((i) => {
            const a = (i / 6) * Math.PI * 2 + tempo * 20;
            return (
              <mesh key={i} position={[Math.cos(a) * 0.22 * faisca, Math.sin(a) * 0.14 * faisca, 0]} rotation={[0, 0, a]}>
                <boxGeometry args={[0.16 * faisca, 0.025, 0.025]} />
                <meshStandardMaterial color="#ffffff" emissive="#fff2a8" emissiveIntensity={3} />
              </mesh>
            );
          })}
        </group>
      ) : null}

      {/* gás na câmara (cresce conforme o pistão desce) */}
      <mesh position={[0, topo + altCamara / 2, 0]} scale={[1, altCamara, 1]}>
        <cylinderGeometry args={[0.4, 0.4, 1, 36]} />
        <meshStandardMaterial color={corFogo} roughness={0.7} emissive={corFogo} emissiveIntensity={chama * 1.6 + mistura * 0.12} />
      </mesh>
      {chama > 0.05 ? (
        <group position={[0, topo + altCamara * 0.1, 0.1]}>
          <Fogo s={tempo} forca={chama} tamanho={1.3} />
        </group>
      ) : null}

      {/* bolinhas entrando: azul = ar, amarelo = combustível */}
      {entrada > 0 && entrada < 1
        ? Array.from({length: 10}, (_, i) => {
            const k = Math.min(1, Math.max(0, entrada * 1.35 - (i / 10) * 0.35));
            if (k <= 0 || k >= 1) return null;
            const [x, y] = caminho(k);
            return (
              <mesh key={i} position={[x, y, 0.02]}>
                <sphereGeometry args={[0.07, 12, 10]} />
                <meshStandardMaterial color={i % 2 ? '#ffd23a' : '#5db8ff'} emissive={i % 2 ? '#ffb000' : '#2e8cff'} emissiveIntensity={0.7} />
              </mesh>
            );
          })
        : null}

      {/* pistão, biela, virabrequim */}
      <mesh position={[0, py, 0]} castShadow>
        <cylinderGeometry args={[0.4, 0.4, PISTAO_ALTURA, 36]} />
        <meshStandardMaterial color="#d8dde6" roughness={0.3} metalness={0.7} {...dest('pistao')} />
      </mesh>
      {[-0.1, 0.0, 0.1].map((dy) => (
        <mesh key={dy} position={[0, py + 0.12 + dy * 0.9, 0]}>
          <cylinderGeometry args={[0.405, 0.405, 0.025, 36]} />
          <meshStandardMaterial color="#59606e" roughness={0.5} metalness={0.5} />
        </mesh>
      ))}
      <Barra a={pino} b={[0, py]} z={0.05} esp={0.14} prof={0.16} cor="#9aa3b2" metal={0.7} rugo={0.35} />
      <mesh position={[0, py, 0.05]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.3, 16]} />
        <meshStandardMaterial color="#6b7382" roughness={0.4} metalness={0.7} />
      </mesh>
      <Barra a={[0, 0]} b={pino} z={0.05} esp={0.2} prof={0.14} cor="#7b8494" metal={0.7} rugo={0.35} />
      <Barra a={[0, 0]} b={[-pino[0] * 0.9, -pino[1] * 0.9]} z={0.05} esp={0.34} prof={0.14} cor="#5e6573" metal={0.6} rugo={0.4} />
      <mesh position={[pino[0], pino[1], 0.05]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 0.3, 16]} />
        <meshStandardMaterial color="#c4cad6" roughness={0.3} metalness={0.8} />
      </mesh>
      <mesh position={[0, 0, 0.25]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.12, 0.12, 0.9, 16]} />
        <meshStandardMaterial color="#8f98a8" roughness={0.35} metalness={0.7} />
      </mesh>

      {/* volante: disco grosso com aro de borracha (a correia passa nele) */}
      <group position={[0, 0, Z_CORREIA]} rotation={[0, 0, -ang]}>
        <mesh rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[VOLANTE_R, VOLANTE_R, 0.14, 48]} />
          <meshStandardMaterial color="#aeb6c4" roughness={0.3} metalness={0.7} {...dest('volante')} />
        </mesh>
        <mesh>
          <torusGeometry args={[VOLANTE_R, 0.06, 12, 48]} />
          <meshStandardMaterial color={correiaCor} roughness={0.8} {...dest('correia')} />
        </mesh>
        {[0, 1, 2, 3].map((i) => (
          <mesh key={i} position={[Math.cos((i * Math.PI) / 2 + 0.4) * 0.3, Math.sin((i * Math.PI) / 2 + 0.4) * 0.3, 0.075]}>
            <cylinderGeometry args={[0.09, 0.09, 0.02, 16]} />
            <meshStandardMaterial color="#2c3038" roughness={0.6} />
          </mesh>
        ))}
        <mesh position={[0.4, 0, 0.08]}>
          <boxGeometry args={[0.2, 0.07, 0.03]} />
          <meshStandardMaterial color="#ff7a1a" roughness={0.4} />
        </mesh>
      </group>

      {/* correia: duas retas escuras com nervuras que andam */}
      {lados.map((l, i) => (
        <group key={i}>
          <Barra a={l.p1} b={l.p2} z={Z_CORREIA} esp={0.1} prof={0.12} cor={correiaCor} rugo={0.8} metal={0.05} emissivo="#ffc61a" forca={foco === 'correia' ? pisca : 0} />
          {Array.from({length: NERV}, (_, j) => {
            const f = (((j + l.dir * fase) % NERV) + NERV) % NERV;
            const k = f / NERV;
            const x = l.p1[0] + (l.p2[0] - l.p1[0]) * k;
            const y = l.p1[1] + (l.p2[1] - l.p1[1]) * k;
            return (
              <mesh key={j} position={[x, y, Z_CORREIA + 0.07]} rotation={[0, 0, -Math.atan2(l.p2[0] - l.p1[0], l.p2[1] - l.p1[1])]}>
                <boxGeometry args={[0.1, 0.035, 0.02]} />
                <meshStandardMaterial color="#6b7280" roughness={0.7} />
              </mesh>
            );
          })}
        </group>
      ))}

      {/* alternador: corpo + polia que gira mais rápido */}
      <group position={[ax, ay, 0]}>
        <mesh position={[0, 0, 0.2]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.38, 0.38, 0.5, 32]} />
          <meshStandardMaterial color="#5d6573" roughness={0.4} metalness={0.6} {...dest('alternador')} />
        </mesh>
        <mesh position={[0, 0, 0.2]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.395, 0.395, 0.08, 32]} />
          <meshStandardMaterial color="#2fae5a" roughness={0.4} emissive="#37d96a" emissiveIntensity={carga * 1.4} />
        </mesh>
        <group position={[0, 0, Z_CORREIA]} rotation={[0, 0, (-ang * VOLANTE_R) / ALT_R]}>
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[ALT_R, ALT_R, 0.14, 24]} />
            <meshStandardMaterial color="#aeb6c4" roughness={0.3} metalness={0.7} />
          </mesh>
          <mesh>
            <torusGeometry args={[ALT_R, 0.05, 10, 24]} />
            <meshStandardMaterial color={correiaCor} roughness={0.8} />
          </mesh>
          <mesh position={[0.1, 0, 0.08]}>
            <boxGeometry args={[0.12, 0.05, 0.03]} />
            <meshStandardMaterial color="#ff7a1a" roughness={0.4} />
          </mesh>
        </group>
      </group>

      {/* cabos do alternador até a bateria; bolinha de energia descendo */}
      <Barra a={[MOTOR_ALTERNADOR[0] - 0.12, MOTOR_ALTERNADOR[1] - 0.4]} b={[MOTOR_BATERIA[0] - 0.12, MOTOR_BATERIA[1] + 0.3]} z={0.25} esp={0.06} prof={0.06} cor="#e0483a" />
      <Barra a={[MOTOR_ALTERNADOR[0] + 0.12, MOTOR_ALTERNADOR[1] - 0.4]} b={[MOTOR_BATERIA[0] + 0.12, MOTOR_BATERIA[1] + 0.3]} z={0.25} esp={0.06} prof={0.06} cor="#22252b" />
      {carga > 0.02 && carga < 1
        ? [0, 1, 2].map((i) => {
            const k = (tempo * 1.5 + i / 3) % 1;
            return (
              <mesh key={i} position={[MOTOR_ALTERNADOR[0] - 0.12, MOTOR_ALTERNADOR[1] - 0.4 - k * 0.95, 0.3]}>
                <sphereGeometry args={[0.06, 10, 8]} />
                <meshStandardMaterial color="#fff2a8" emissive="#ffd23a" emissiveIntensity={2} />
              </mesh>
            );
          })
        : null}

      {/* bateria com 4 luzinhas que enchem */}
      <group position={[MOTOR_BATERIA[0], MOTOR_BATERIA[1], 0.25]}>
        <mesh castShadow>
          <boxGeometry args={[1.1, 0.6, 0.5]} />
          <meshStandardMaterial color="#2f6fd0" roughness={0.45} metalness={0.2} {...dest('bateria')} />
        </mesh>
        {[-0.3, 0.3].map((x, i) => (
          <mesh key={x} position={[x, 0.36, 0]}>
            <cylinderGeometry args={[0.07, 0.07, 0.12, 12]} />
            <meshStandardMaterial color={i ? '#22252b' : '#e0483a'} roughness={0.4} metalness={0.5} />
          </mesh>
        ))}
        {[0, 1, 2, 3].map((i) => {
          const ligada = carga > (i + 0.5) / 4;
          return (
            <mesh key={i} position={[-0.39 + i * 0.26, 0, 0.26]}>
              <boxGeometry args={[0.2, 0.3, 0.03]} />
              <meshStandardMaterial color={ligada ? '#7dff9a' : '#1d2f55'} emissive={ligada ? '#37d96a' : '#000000'} emissiveIntensity={ligada ? 1.6 : 0} roughness={0.5} />
            </mesh>
          );
        })}
      </group>
    </group>
  );
};
