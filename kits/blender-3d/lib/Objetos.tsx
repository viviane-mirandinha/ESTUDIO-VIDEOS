// Kit cotidiano.explicado · de cotidiano.explicado (@cotidiano.explicado) · não pode ser revendido nem usado para criar um produto parecido (LICENCA.md).
import React from 'react';
import * as THREE from 'three';

/**
 * Objetos prontos para as histórias (modo simples). Todos são função do
 * segundo atual quando se mexem (`s`). Use antes de inventar um objeto novo;
 * se inventar, acrescente aqui para os próximos vídeos.
 */

type V3 = [number, number, number];

const sorteio = (i: number, k: number) => {
  const v = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
  return v - Math.floor(v);
};

const Brilhante: React.FC<{cor: string; rug?: number}> = ({cor, rug = 0.3}) => <meshPhysicalMaterial color={cor} roughness={rug} clearcoat={1} clearcoatRoughness={0.1} />;

// ------------------------------------------------------------- carro detalhado

/**
 * Onde fica o vão do motor do `CarroDetalhado` (coordenadas do carro, frente
 * para +x). Para o motor entrar "justinho", escale o motor para caber em
 * `tamanho` e leve o centro dele até `centro` (veja `encaixar` em tempo.ts).
 */
export const BAIA_MOTOR = {centro: [1.0, 0.72, 0] as V3, tamanho: [0.95, 0.42, 1.18] as V3};

/**
 * Carro com capô que abre e vão do motor de verdade. `capo` 0 → 1 abre;
 * `giroRodas` gira as rodas (radianos); `motor` vai dentro do vão;
 * `motorista` vai no banco; `faroisAcesos` acende os faróis.
 */
export const CarroDetalhado: React.FC<{
  cor?: string;
  capo?: number;
  giroRodas?: number;
  motor?: React.ReactNode;
  motorista?: React.ReactNode;
  faroisAcesos?: boolean;
  semRodas?: boolean;
}> = ({cor = '#e2463a', capo = 0, giroRodas = 0, motor, motorista, faroisAcesos = false, semRodas = false}) => (
  <group>
    {/* parte de baixo: laterais, traseira e para-choques (o meio da frente é o vão do motor) */}
    <mesh position={[-0.55, 0.58, 0]} castShadow receiveShadow>
      <boxGeometry args={[1.9, 0.52, 1.5]} />
      <Brilhante cor={cor} />
    </mesh>
    {[-1, 1].map((l) => (
      <mesh key={l} position={[1.0, 0.58, l * 0.7]} castShadow>
        <boxGeometry args={[1.0, 0.52, 0.1]} />
        <Brilhante cor={cor} />
      </mesh>
    ))}
    <mesh position={[1.47, 0.58, 0]} castShadow>
      <boxGeometry args={[0.08, 0.52, 1.5]} />
      <Brilhante cor={cor} />
    </mesh>
    {/* vão do motor: fundo escuro */}
    <mesh position={[1.0, 0.36, 0]} receiveShadow>
      <boxGeometry args={[0.95, 0.06, 1.3]} />
      <meshStandardMaterial color="#1b1c20" roughness={0.8} />
    </mesh>
    {/* para-choques e grade */}
    {[1.55, -1.55].map((x) => (
      <mesh key={x} position={[x, 0.42, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <capsuleGeometry args={[0.1, 1.3, 8, 16]} />
        <meshStandardMaterial color="#d7d9de" metalness={0.7} roughness={0.25} />
      </mesh>
    ))}
    <mesh position={[1.52, 0.62, 0]}>
      <boxGeometry args={[0.04, 0.2, 0.7]} />
      <meshStandardMaterial color="#2a2b30" roughness={0.6} />
    </mesh>
    {/* faróis e lanternas */}
    {[-0.52, 0.52].map((z) => (
      <group key={z}>
        <mesh position={[1.53, 0.66, z]}>
          <cylinderGeometry args={[0.1, 0.1, 0.05, 20]} />
          <meshStandardMaterial color="#fff8e0" emissive="#ffe9a8" emissiveIntensity={faroisAcesos ? 2.5 : 0.4} />
        </mesh>
        <mesh position={[-1.52, 0.66, z]}>
          <boxGeometry args={[0.04, 0.12, 0.26]} />
          <meshStandardMaterial color="#c4161c" emissive="#ff2a2a" emissiveIntensity={faroisAcesos ? 1.2 : 0.3} />
        </mesh>
      </group>
    ))}
    {/* cabine: colunas, teto e vidros */}
    <mesh position={[-0.35, 1.38, 0]} castShadow>
      <boxGeometry args={[1.3, 0.07, 1.36]} />
      <Brilhante cor={cor} />
    </mesh>
    {[
      [0.3, -0.3],
      [-1.0, 0.25],
    ].map(([x, inc]) =>
      [-0.64, 0.64].map((z) => (
        <mesh key={`${x}${z}`} position={[x, 1.1, z]} rotation={[0, 0, inc]} castShadow>
          <boxGeometry args={[0.07, 0.6, 0.07]} />
          <Brilhante cor={cor} />
        </mesh>
      )),
    )}
    <mesh position={[-0.35, 1.1, 0]}>
      <boxGeometry args={[1.28, 0.52, 1.3]} />
      <meshPhysicalMaterial color="#9fc6dc" roughness={0.05} transparent opacity={0.28} />
    </mesh>
    {/* retrovisores e maçanetas */}
    {[-1, 1].map((l) => (
      <group key={l}>
        <mesh position={[0.32, 0.9, l * 0.82]}>
          <boxGeometry args={[0.12, 0.1, 0.14]} />
          <Brilhante cor={cor} />
        </mesh>
        <mesh position={[-0.4, 0.72, l * 0.76]}>
          <boxGeometry args={[0.16, 0.04, 0.02]} />
          <meshStandardMaterial color="#d7d9de" metalness={0.7} roughness={0.25} />
        </mesh>
      </group>
    ))}
    {/* capô: gira na dobradiça perto do para-brisa */}
    <group position={[0.5, 0.86, 0]} rotation={[0, 0, capo * 1.15]}>
      <mesh position={[0.5, 0, 0]} castShadow>
        <boxGeometry args={[1.02, 0.05, 1.5]} />
        <Brilhante cor={cor} />
      </mesh>
    </group>
    {motor ? <group position={BAIA_MOTOR.centro}>{motor}</group> : null}
    {motorista ? <group position={[-0.3, 0.32, 0.3]}>{motorista}</group> : null}
    {/* rodas com calota */}
    {!semRodas
      ? [
          [0.95, 0.76],
          [0.95, -0.76],
          [-1.0, 0.76],
          [-1.0, -0.76],
        ].map(([x, z]) => (
          <group key={`${x}${z}`} position={[x, 0.36, z]} rotation={[0, 0, -giroRodas]}>
            <mesh rotation={[Math.PI / 2, 0, 0]} castShadow>
              <cylinderGeometry args={[0.36, 0.36, 0.26, 28]} />
              <meshStandardMaterial color="#1c1c20" roughness={0.85} />
            </mesh>
            <mesh rotation={[Math.PI / 2, 0, 0]}>
              <cylinderGeometry args={[0.2, 0.2, 0.28, 20]} />
              <meshStandardMaterial color="#d7d9de" metalness={0.7} roughness={0.25} />
            </mesh>
            {[0, 1, 2, 3, 4].map((n) => (
              <mesh key={n} rotation={[0, 0, (n * Math.PI * 2) / 5]} position={[0, 0, (z > 0 ? 1 : -1) * 0.15]}>
                <boxGeometry args={[0.05, 0.34, 0.02]} />
                <meshStandardMaterial color="#9a9ea6" metalness={0.6} roughness={0.3} />
              </mesh>
            ))}
          </group>
        ))
      : null}
    {/* escapamento */}
    <mesh position={[-1.62, 0.3, 0.45]} rotation={[0, 0, Math.PI / 2]}>
      <cylinderGeometry args={[0.06, 0.06, 0.25, 12]} />
      <meshStandardMaterial color="#9a9ea6" metalness={0.7} roughness={0.3} />
    </mesh>
  </group>
);

// ------------------------------------------------------------- objetos de casa

/** A alça do `Galao` (coordenadas do galão): é o ponto que fica na mão e o eixo do tombo. */
export const ALCA_GALAO: V3 = [0, 0.4, -0.06];

/** Ponta do bico do `Galao` (coordenadas do galão) para uma inclinação: é dali que o líquido sai. */
export const bicoDoGalao = (inclina = 0): V3 => {
  // o bico gira em volta da alça
  const y = 0.4 - ALCA_GALAO[1];
  const z = 0.24 - ALCA_GALAO[2];
  return [0, ALCA_GALAO[1] + y * Math.cos(inclina) - z * Math.sin(inclina), ALCA_GALAO[2] + y * Math.sin(inclina) + z * Math.cos(inclina)];
};

/**
 * Galão em pé com alça em cima e bico na frente (+z). `inclina` (radianos)
 * tomba para a frente girando em volta da alça (a mão não solta), para
 * despejar pelo bico. O jato sai de `bicoDoGalao`. Na mão, desloque o galão
 * por −ALCA_GALAO para a alça ficar na palma.
 */
export const Galao: React.FC<{cor?: string; inclina?: number; brilho?: number}> = ({cor = '#e2312b', inclina = 0, brilho = 0}) => (
  <group position={ALCA_GALAO} rotation={[inclina, 0, 0]}>
    <group position={[-ALCA_GALAO[0], -ALCA_GALAO[1], -ALCA_GALAO[2]]}>
      <mesh castShadow>
        <boxGeometry args={[0.26, 0.56, 0.42]} />
        <meshStandardMaterial color={cor} roughness={0.45} emissive="#ffb020" emissiveIntensity={brilho * 0.55} />
      </mesh>
      {/* alça em cima, atravessada */}
      <mesh position={[0, 0.3, -0.06]} rotation={[0, Math.PI / 2, 0]}>
        <torusGeometry args={[0.11, 0.032, 10, 24, Math.PI]} />
        <meshStandardMaterial color={cor} roughness={0.45} />
      </mesh>
      {/* bico na frente, apontando para cima e para a frente */}
      <mesh position={[0, 0.33, 0.15]} rotation={[0.75, 0, 0]}>
        <cylinderGeometry args={[0.035, 0.055, 0.2, 14]} />
        <meshStandardMaterial color="#2a2a30" roughness={0.5} />
      </mesh>
    </group>
  </group>
);

/** Vasilha/panela rasa (onde se testa a primeira ideia). */
export const Vasilha: React.FC<{cor?: string; raio?: number; liquido?: number; corLiquido?: string}> = ({cor = '#3a3d44', raio = 0.42, liquido = 0, corLiquido = '#e9c46a'}) => (
  <group>
    <mesh castShadow receiveShadow>
      <cylinderGeometry args={[raio, raio * 0.8, raio * 0.3, 32, 1, true]} />
      <meshStandardMaterial color={cor} metalness={0.6} roughness={0.35} side={THREE.DoubleSide} />
    </mesh>
    <mesh position={[0, -raio * 0.15, 0]}>
      <cylinderGeometry args={[raio * 0.8, raio * 0.8, 0.02, 32]} />
      <meshStandardMaterial color={cor} metalness={0.6} roughness={0.35} />
    </mesh>
    {liquido > 0 ? (
      <mesh position={[0, -raio * 0.15 + raio * 0.25 * liquido, 0]}>
        <cylinderGeometry args={[raio * (0.8 + 0.18 * liquido), raio * 0.8, 0.02, 32]} />
        <meshPhysicalMaterial color={corLiquido} roughness={0.1} clearcoat={1} transparent opacity={0.9} />
      </mesh>
    ) : null}
  </group>
);

/** Fogo: chamas laranja que tremulam. `forca` 0 → 1 (cresce). */
export const Fogo: React.FC<{s: number; forca?: number; tamanho?: number}> = ({s, forca = 1, tamanho = 1}) => (
  <group scale={tamanho}>
    {Array.from({length: 9}, (_, i) => {
      const a = (i / 9) * Math.PI * 2;
      const pulsa = 0.75 + 0.25 * Math.sin(s * 14 + i * 2.1);
      return (
        <mesh key={i} position={[Math.cos(a) * 0.18 * forca, 0.3 * forca * pulsa, Math.sin(a) * 0.18 * forca]} scale={[forca, forca * pulsa * (1 + (i % 3) * 0.3), forca]}>
          <coneGeometry args={[0.16, 0.7, 10]} />
          <meshStandardMaterial color={i % 2 ? '#ff7a1a' : '#ffb020'} emissive={i % 2 ? '#ff4a00' : '#ff8a00'} emissiveIntensity={0.9} transparent opacity={0.92} />
        </mesh>
      );
    })}
  </group>
);

/** Fumaça subindo em bolotas. `forca` 0 → 1. */
export const Fumaca: React.FC<{s: number; forca?: number; cor?: string}> = ({s, forca = 1, cor = '#8e8e96'}) => (
  <group>
    {Array.from({length: 10}, (_, i) => {
      const vida = (s * 0.6 + sorteio(i, 1)) % 1;
      return (
        <mesh key={i} position={[(sorteio(i, 2) - 0.5) * 0.4 + vida * 0.3, vida * 1.6, (sorteio(i, 3) - 0.5) * 0.4]}>
          <sphereGeometry args={[0.12 + vida * 0.25, 14, 10]} />
          <meshStandardMaterial color={cor} roughness={1} transparent opacity={forca * 0.7 * (1 - vida)} />
        </mesh>
      );
    })}
  </group>
);

/** Jato de líquido caindo de `de` até `ate` (pontos do mundo), com gotas correndo. */
export const JatoLiquido: React.FC<{s: number; de: V3; ate: V3; cor?: string; forca?: number}> = ({s, de, ate, cor = '#e9c46a', forca = 1}) => (
  <group>
    {forca > 0
      ? Array.from({length: 16}, (_, i) => {
          const k = ((s * 2.2 + i / 16) % 1);
          const x = de[0] + (ate[0] - de[0]) * k;
          const z = de[2] + (ate[2] - de[2]) * k;
          const y = de[1] + (ate[1] - de[1]) * k * k; // cai acelerando
          return (
            <mesh key={i} position={[x, y, z]} scale={[1, 1.6, 1]}>
              <sphereGeometry args={[0.045 * forca, 10, 8]} />
              <meshPhysicalMaterial color={cor} roughness={0.1} clearcoat={1} transparent opacity={0.9} />
            </mesh>
          );
        })
      : null}
  </group>
);

// ------------------------------------------------------------- veículos do personagem

/** Bicicleta vermelha (frente para +z). Sente o personagem em y + 0.2, z − 0.32. */
export const Bicicleta: React.FC = () => {
  const roda = (z: number) => (
    <group position={[0, 0.55, z]} rotation={[0, Math.PI / 2, 0]}>
      <mesh castShadow>
        <torusGeometry args={[0.5, 0.06, 14, 40]} />
        <meshStandardMaterial color="#1e1e22" roughness={0.8} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.07, 0.07, 0.12, 16]} />
        <meshStandardMaterial color="#c9ccd2" metalness={0.6} roughness={0.3} />
      </mesh>
    </group>
  );
  const tubo = (de: V3, ate: V3, r = 0.04) => {
    const meio: V3 = [(de[0] + ate[0]) / 2, (de[1] + ate[1]) / 2, (de[2] + ate[2]) / 2];
    const dy = ate[1] - de[1];
    const dz = ate[2] - de[2];
    return (
      <mesh position={meio} rotation={[Math.atan2(dz, dy), 0, 0]} castShadow>
        <cylinderGeometry args={[r, r, Math.hypot(dy, dz), 12]} />
        <meshStandardMaterial color="#e2312b" roughness={0.35} metalness={0.2} />
      </mesh>
    );
  };
  return (
    <group>
      {roda(-0.85)}
      {roda(0.85)}
      {tubo([0, 0.55, -0.85], [0, 0.98, -0.2])}
      {tubo([0, 0.98, -0.2], [0, 1.0, 0.6])}
      {tubo([0, 0.55, -0.85], [0, 0.55, 0.05])}
      {tubo([0, 0.55, 0.05], [0, 0.98, -0.2])}
      {tubo([0, 0.55, 0.05], [0, 1.0, 0.6])}
      {tubo([0, 0.55, 0.85], [0, 1.25, 0.62], 0.035)}
      <mesh position={[0, 1.04, -0.22]} castShadow>
        <boxGeometry args={[0.2, 0.06, 0.34]} />
        <meshStandardMaterial color="#1e1e22" roughness={0.6} />
      </mesh>
      <mesh position={[0, 1.27, 0.62]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <cylinderGeometry args={[0.03, 0.03, 0.7, 12]} />
        <meshStandardMaterial color="#2a2a30" roughness={0.5} />
      </mesh>
    </group>
  );
};

/** Banco de carro com volante (para cenas de "dirigindo" de perto). */
export const Volante: React.FC<{giro?: number}> = ({giro = 0}) => (
  <group>
    <mesh position={[0, 0.42, -0.1]} castShadow receiveShadow>
      <boxGeometry args={[0.9, 0.16, 0.8]} />
      <meshStandardMaterial color="#3a3a42" roughness={0.8} />
    </mesh>
    <mesh position={[0, 1.0, -0.5]} rotation={[-0.15, 0, 0]} castShadow>
      <boxGeometry args={[0.9, 1.1, 0.16]} />
      <meshStandardMaterial color="#3a3a42" roughness={0.8} />
    </mesh>
    <group position={[0, 1.35, 0.78]} rotation={[0.45, 0, 0]}>
      <group rotation={[0, 0, giro]}>
        <mesh castShadow>
          <torusGeometry args={[0.3, 0.04, 12, 36]} />
          <meshStandardMaterial color="#1e1e22" roughness={0.5} />
        </mesh>
        <mesh>
          <boxGeometry args={[0.56, 0.05, 0.04]} />
          <meshStandardMaterial color="#1e1e22" roughness={0.5} />
        </mesh>
      </group>
      <mesh position={[0, 0, -0.25]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 0.5, 12]} />
        <meshStandardMaterial color="#1e1e22" roughness={0.5} />
      </mesh>
    </group>
  </group>
);
