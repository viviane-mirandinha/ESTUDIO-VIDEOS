import React from 'react';
import * as THREE from 'three';

/**
 * Turbina de avião (fan na frente, carcaça em volta, cone no centro).
 * O eixo da turbina aponta para +z (a "boca" olha para a câmera padrão).
 * `giro` = ângulo das pás em radianos (use s * velocidade). Cada pá é um <mesh> próprio.
 * `brilho` 0 → 1 acende o miolo (calor/força).
 */
export const Turbina: React.FC<{giro?: number; pas?: number; brilho?: number; cor?: string}> = ({giro = 0, pas = 14, brilho = 0, cor = '#b9c0cc'}) => {
  const R = 1.5;
  const quente = new THREE.Color('#2b2f38').lerp(new THREE.Color('#ff8a2a'), Math.min(1, Math.max(0, brilho)));
  return (
    <group>
      {/* carcaça: tubo aberto + aro grosso na boca */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, -0.1]} castShadow>
        <cylinderGeometry args={[R + 0.18, R + 0.18, 2.4, 48, 1, true]} />
        <meshStandardMaterial color={cor} roughness={0.35} metalness={0.5} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0, 0, 1.1]} castShadow>
        <torusGeometry args={[R + 0.18, 0.12, 16, 48]} />
        <meshStandardMaterial color="#dfe3ea" roughness={0.3} metalness={0.5} />
      </mesh>
      {/* fundo escuro por dentro (dá profundidade) */}
      <mesh position={[0, 0, -0.5]}>
        <circleGeometry args={[R, 40]} />
        <meshStandardMaterial color={quente} roughness={0.6} emissive={quente} emissiveIntensity={0.6 * brilho} />
      </mesh>
      {/* pás girando */}
      <group position={[0, 0, 0.3]} rotation={[0, 0, giro]}>
        {Array.from({length: pas}, (_, i) => {
          const a = (i / pas) * Math.PI * 2;
          return (
            <group key={i} rotation={[0, 0, a]}>
              <mesh position={[0.8, 0, 0]} rotation={[0.45, 0, 0]} castShadow>
                <boxGeometry args={[1.3, 0.26, 0.04]} />
                <meshStandardMaterial color="#8f98a8" roughness={0.3} metalness={0.7} />
              </mesh>
            </group>
          );
        })}
        {/* cone do centro */}
        <mesh position={[0, 0, 0.2]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <coneGeometry args={[0.38, 0.7, 24]} />
          <meshStandardMaterial color="#e8ebf0" roughness={0.25} metalness={0.6} />
        </mesh>
      </group>
    </group>
  );
};
