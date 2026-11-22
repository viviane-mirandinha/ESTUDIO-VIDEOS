import React from 'react';

type V3 = [number, number, number];

/** Eixo dos pedais (z, y) na `BicicletaPedal` e tamanho da manivela. */
export const EIXO_PEDAL = {z: 0.05, y: 0.55, raio: 0.17, meiaLargura: 0.2};

/** Onde fica o pedal (z, y) quando a manivela está no ângulo `a` (0 = em cima; cresce girando para a frente). */
export const pedalEm = (a: number): {z: number; y: number} => ({z: EIXO_PEDAL.z + EIXO_PEDAL.raio * Math.sin(a), y: EIXO_PEDAL.y + EIXO_PEDAL.raio * Math.cos(a)});

const COR_QUADRO = '#e2312b';

/**
 * Bicicleta vermelha com roda, raios, manivelas e pedais que giram (frente para +z).
 * `roda` = ângulo das rodas (radianos, positivo = rolando para a frente); `pedal` = ângulo da manivela.
 * Os pedais ficam sempre na horizontal (cada um é um `<mesh>` próprio).
 */
export const BicicletaPedal: React.FC<{roda?: number; pedal?: number}> = ({roda = 0, pedal = 0}) => {
  const rodaPeca = (z: number) => (
    <group position={[0, 0.55, z]}>
      <group rotation={[roda, 0, 0]}>
        <group rotation={[0, Math.PI / 2, 0]}>
          <mesh castShadow>
            <torusGeometry args={[0.5, 0.06, 14, 40]} />
            <meshStandardMaterial color="#1e1e22" roughness={0.8} />
          </mesh>
        </group>
        <mesh rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.07, 0.07, 0.12, 16]} />
          <meshStandardMaterial color="#c9ccd2" metalness={0.6} roughness={0.3} />
        </mesh>
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
          <mesh key={i} rotation={[(i * Math.PI) / 8, 0, 0]}>
            <boxGeometry args={[0.02, 0.96, 0.02]} />
            <meshStandardMaterial color="#c9ccd2" metalness={0.5} roughness={0.35} />
          </mesh>
        ))}
        {/* marca amarela no pneu: deixa o giro da roda visível */}
        <mesh position={[0, 0.5, 0]}>
          <boxGeometry args={[0.17, 0.09, 0.09]} />
          <meshStandardMaterial color="#ffd23f" roughness={0.5} />
        </mesh>
      </group>
    </group>
  );
  const tubo = (de: V3, ate: V3, r = 0.04) => {
    const meio: V3 = [(de[0] + ate[0]) / 2, (de[1] + ate[1]) / 2, (de[2] + ate[2]) / 2];
    const dy = ate[1] - de[1];
    const dz = ate[2] - de[2];
    return (
      <mesh position={meio} rotation={[Math.atan2(dz, dy), 0, 0]} castShadow>
        <cylinderGeometry args={[r, r, Math.hypot(dy, dz), 12]} />
        <meshStandardMaterial color={COR_QUADRO} roughness={0.35} metalness={0.2} />
      </mesh>
    );
  };
  const manivela = (lado: 1 | -1, a: number) => {
    const p = pedalEm(a);
    const x = lado * EIXO_PEDAL.meiaLargura;
    const meioZ = (EIXO_PEDAL.z + p.z) / 2;
    const meioY = (EIXO_PEDAL.y + p.y) / 2;
    return (
      <group key={lado}>
        <mesh position={[x, meioY, meioZ]} rotation={[Math.atan2(p.z - EIXO_PEDAL.z, p.y - EIXO_PEDAL.y), 0, 0]} castShadow>
          <boxGeometry args={[0.04, EIXO_PEDAL.raio * 2, 0.04]} />
          <meshStandardMaterial color="#c9ccd2" metalness={0.6} roughness={0.3} />
        </mesh>
        <mesh position={[x + lado * 0.05, p.y, p.z]} castShadow>
          <boxGeometry args={[0.14, 0.035, 0.2]} />
          <meshStandardMaterial color="#2a2a30" roughness={0.6} />
        </mesh>
      </group>
    );
  };
  return (
    <group>
      {rodaPeca(-0.85)}
      {rodaPeca(0.85)}
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
      {/* eixo dos pedais */}
      <mesh position={[0, EIXO_PEDAL.y, EIXO_PEDAL.z]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.04, 0.04, EIXO_PEDAL.meiaLargura * 2, 12]} />
        <meshStandardMaterial color="#c9ccd2" metalness={0.6} roughness={0.3} />
      </mesh>
      {manivela(1, pedal)}
      {manivela(-1, pedal + Math.PI)}
    </group>
  );
};
