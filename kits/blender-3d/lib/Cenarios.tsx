import React, {useMemo} from 'react';
import * as THREE from 'three';

/**
 * Os cenários do modo simples. Cada um é um lugar fixo onde a máquina é
 * montada no centro (x = 0, z = 0). A câmera passeia; o cenário não muda.
 *
 * - `Garagem`: garagem moderna escura, piso de concreto, fitas de luz.
 * - `Atelie`: ateliê de inventor com janelão para a cidade e bancada de madeira.
 * - `Infinito`: estúdio de fundo infinito, uma cor só, sem cantos.
 */

const sorteio = (i: number, k: number) => {
  const v = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
  return v - Math.floor(v);
};

const Caixa: React.FC<{pos: [number, number, number]; tam: [number, number, number]; cor: string; brilho?: number; rugosidade?: number; metal?: number}> = ({
  pos,
  tam,
  cor,
  brilho = 0,
  rugosidade = 0.8,
  metal = 0,
}) => (
  <mesh position={pos} castShadow receiveShadow>
    <boxGeometry args={tam} />
    <meshStandardMaterial color={cor} roughness={rugosidade} metalness={metal} emissive={brilho ? cor : '#000000'} emissiveIntensity={brilho} />
  </mesh>
);

// ------------------------------------------------------------- garagem

export const Garagem: React.FC = () => (
  <group>
    {/* piso de concreto polido e parede de ripas escuras */}
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[40, 40]} />
      <meshStandardMaterial color="#a9a6a0" roughness={0.45} metalness={0.05} />
    </mesh>
    <Caixa pos={[0, 4, -4]} tam={[24, 8, 0.2]} cor="#3d424b" />
    {Array.from({length: 40}, (_, i) => (
      <Caixa key={i} pos={[-9.75 + i * 0.5, 3.4, -3.85]} tam={[0.22, 6.8, 0.1]} cor="#4b515b" rugosidade={0.6} />
    ))}
    {/* fita de luz no alto da parede e no rodapé */}
    <Caixa pos={[0, 6.6, -3.75]} tam={[20, 0.06, 0.06]} cor="#fff2d8" brilho={2.5} />
    <Caixa pos={[0, 0.06, -3.75]} tam={[20, 0.05, 0.05]} cor="#ffcf8a" brilho={1.5} />
    {/* portão de enrolar à direita */}
    {Array.from({length: 22}, (_, i) => (
      <Caixa key={`p${i}`} pos={[6.2, 0.15 + i * 0.22, -3.7]} tam={[4.2, 0.18, 0.08]} cor="#8d9097" metal={0.5} rugosidade={0.4} />
    ))}
    {/* estante de metal com caixas à esquerda */}
    {[0.5, 1.6, 2.7].map((y) => (
      <Caixa key={y} pos={[-5.6, y, -3.2]} tam={[3, 0.06, 0.8]} cor="#1c1d21" metal={0.6} rugosidade={0.4} />
    ))}
    {[-7.05, -4.15].map((x) => (
      <Caixa key={x} pos={[x, 1.5, -3.2]} tam={[0.06, 3, 0.8]} cor="#1c1d21" metal={0.6} rugosidade={0.4} />
    ))}
    {Array.from({length: 9}, (_, i) => (
      <Caixa
        key={`c${i}`}
        pos={[-6.6 + (i % 3) * 1.0, 0.78 + Math.floor(i / 3) * 1.1, -3.2]}
        tam={[0.7, 0.5, 0.6]}
        cor={['#e2312b', '#f2c230', '#3d7bd9', '#e9e4da'][i % 4]}
        rugosidade={0.6}
      />
    ))}
  </group>
);

// ------------------------------------------------------------- ateliê

const usaCeu = () =>
  useMemo(() => {
    // fora do navegador (o "assar" do Blender roda no Node) não há canvas: o céu vira cor lisa
    if (typeof document === 'undefined') return null;
    const c = document.createElement('canvas');
    c.width = 16;
    c.height = 256;
    const g = c.getContext('2d')!;
    const grad = g.createLinearGradient(0, 0, 0, 256);
    grad.addColorStop(0, '#9cc3e6');
    grad.addColorStop(0.6, '#f3d9b8');
    grad.addColorStop(1, '#f0b98a');
    g.fillStyle = grad;
    g.fillRect(0, 0, 16, 256);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);

export const Atelie: React.FC = () => {
  const ceu = usaCeu();
  return (
    <group>
      {/* piso de tábuas */}
      {Array.from({length: 30}, (_, i) => (
        <mesh key={i} position={[-15 + i + 0.5, 0, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[0.97, 40]} />
          <meshStandardMaterial color={['#c99c6b', '#bf9161', '#d1a776'][i % 3]} roughness={0.75} />
        </mesh>
      ))}
      {/* parede creme com janelão */}
      <Caixa pos={[-7.5, 4, -4]} tam={[9, 8, 0.2]} cor="#efe6d6" />
      <Caixa pos={[7.5, 4, -4]} tam={[9, 8, 0.2]} cor="#efe6d6" />
      <Caixa pos={[0, 0.6, -4]} tam={[6, 1.2, 0.2]} cor="#efe6d6" />
      <Caixa pos={[0, 7.4, -4]} tam={[6, 1.2, 0.2]} cor="#efe6d6" />
      {/* céu e cidade lá fora */}
      <mesh position={[0, 4, -9]}>
        <planeGeometry args={[20, 12]} />
        <meshBasicMaterial map={ceu} color={ceu ? '#ffffff' : '#f3d9b8'} />
      </mesh>
      {Array.from({length: 26}, (_, i) => (
        <mesh key={i} position={[-6 + i * 0.5, (1.5 + sorteio(i, 1) * 3.5) / 2 + 0.8, -8.5 + sorteio(i, 2)]}>
          <boxGeometry args={[0.45, 1.5 + sorteio(i, 1) * 3.5, 0.4]} />
          <meshBasicMaterial color={['#c7b9ac', '#b8aa9f', '#d4c6b8'][i % 3]} />
        </mesh>
      ))}
      {/* caixilhos pretos do janelão */}
      {[-3, -1, 1, 3].map((x) => (
        <Caixa key={x} pos={[x, 4, -3.95]} tam={[0.1, 5.6, 0.12]} cor="#1c1c20" metal={0.4} rugosidade={0.4} />
      ))}
      {[1.2, 4, 6.8].map((y) => (
        <Caixa key={`h${y}`} pos={[0, y, -3.95]} tam={[6, 0.1, 0.12]} cor="#1c1c20" metal={0.4} rugosidade={0.4} />
      ))}
      {/* bancada de madeira com ferramentas e um vaso de planta */}
      <Caixa pos={[5.6, 1.5, -2.6]} tam={[4, 0.12, 1.2]} cor="#8a5a34" rugosidade={0.6} />
      {[3.8, 7.4].map((x) => (
        <Caixa key={x} pos={[x, 0.72, -2.6]} tam={[0.12, 1.44, 1.0]} cor="#2a2a30" metal={0.4} />
      ))}
      <Caixa pos={[4.9, 1.75, -2.7]} tam={[0.8, 0.36, 0.4]} cor="#e2312b" />
      <Caixa pos={[6.1, 1.62, -2.5]} tam={[0.9, 0.12, 0.12]} cor="#f2c230" />
      <group position={[7.0, 1.56, -2.7]}>
        <mesh castShadow position={[0, 0.2, 0]}>
          <cylinderGeometry args={[0.22, 0.17, 0.4, 20]} />
          <meshStandardMaterial color="#d9cbb6" roughness={0.8} />
        </mesh>
        {[0, 1, 2, 3, 4].map((k) => (
          <mesh key={k} castShadow position={[Math.cos(k * 1.3) * 0.15, 0.55 + (k % 2) * 0.15, Math.sin(k * 1.3) * 0.15]}>
            <sphereGeometry args={[0.2, 16, 12]} />
            <meshStandardMaterial color={['#4f7d3a', '#5f9246', '#3f6a2f'][k % 3]} roughness={0.8} />
          </mesh>
        ))}
      </group>
      {/* luminária pendente */}
      <mesh position={[-4.5, 6.2, -1.5]}>
        <cylinderGeometry args={[0.02, 0.02, 3.6, 8]} />
        <meshStandardMaterial color="#1c1c20" />
      </mesh>
      <mesh position={[-4.5, 4.3, -1.5]} castShadow>
        <coneGeometry args={[0.5, 0.45, 24, 1, true]} />
        <meshStandardMaterial color="#1c1c20" side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[-4.5, 4.15, -1.5]}>
        <sphereGeometry args={[0.14, 16, 12]} />
        <meshStandardMaterial color="#fff1d0" emissive="#fff1d0" emissiveIntensity={3} />
      </mesh>
    </group>
  );
};

// ------------------------------------------------------------- fundo infinito

export const Infinito: React.FC<{cor?: string}> = ({cor = '#f2dcc2'}) => {
  // piso e parede ligados por uma curva (sem canto), como estúdio de fotografia
  const geo = useMemo(() => {
    const pts: THREE.Vector2[] = [];
    const R = 3;
    pts.push(new THREE.Vector2(14, 0));
    for (let i = 0; i <= 16; i++) {
      const a = (i / 16) * (Math.PI / 2);
      pts.push(new THREE.Vector2(-R * Math.sin(a), R - R * Math.cos(a)));
    }
    pts.push(new THREE.Vector2(-R, 14));
    // o perfil (z, y) vira uma fita larga ao longo de x
    const g = new THREE.BufferGeometry();
    const largura = 40;
    const vs: number[] = [];
    const idx: number[] = [];
    pts.forEach((p, i) => {
      vs.push(-largura / 2, p.y, p.x, largura / 2, p.y, p.x);
      if (i < pts.length - 1) {
        const a = i * 2;
        idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
      }
    });
    g.setAttribute('position', new THREE.Float32BufferAttribute(vs, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }, []);
  return (
    <group>
      <mesh geometry={geo} position={[0, 0, -1]} receiveShadow>
        <meshStandardMaterial color={cor} roughness={0.95} side={THREE.DoubleSide} />
      </mesh>
      {/* palco redondo onde a máquina fica */}
      <mesh position={[0.6, 0.06, 0]} receiveShadow castShadow>
        <cylinderGeometry args={[2.2, 2.3, 0.12, 64]} />
        <meshStandardMaterial color="#fbf4ea" roughness={0.6} />
      </mesh>
    </group>
  );
};
