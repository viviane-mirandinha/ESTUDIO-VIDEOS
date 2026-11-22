// Exemplo: cena 3D "vitrine" (personagem + carro + galão). Só descreve o 3D de cada segundo.
// Regra do kit: este arquivo exporta DURACAO (segundos) e quadro3D(s). Sem legenda aqui:
// legenda, voz e música entram depois pelo Estúdio.
import React from 'react';
import {
  BAIA_MOTOR, CarroDetalhado, Fumaca, Galao, ALCA_GALAO, bicoDoGalao, pontoNaMao, JatoLiquido,
  PERSONAGEM_KIRMASK, POSE, Personagem, Garagem, Vasilha, cameraEm, desanimar, desde, despejar,
  encaixar, juntar, negar, pular, suave, tremer,
  type Camera, type Expressao, type Plano, type Quadro3D,
} from '@estudio3d';

export const DURACAO = 10.5;

const T = {negar: 2.0, despeja: 3.6, capo: 5.2, encaixa: 5.8, fecha: 7.0, liga: 7.5, pula: 8.9};

/** Um motor pequeno feito para caber no vão do carro (BAIA_MOTOR.tamanho). */
const MotorMini: React.FC = () => {
  const [l, a, p] = BAIA_MOTOR.tamanho;
  return (
    <group>
      <mesh position={[0, -a / 2 + 0.12, 0]} castShadow>
        <boxGeometry args={[l * 0.9, 0.24, p * 0.85]} />
        <meshStandardMaterial color="#2c3038" roughness={0.5} metalness={0.3} />
      </mesh>
      {[-0.33, -0.11, 0.11, 0.33].map((z) => (
        <mesh key={z} position={[0, 0.05, z * p]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 0.2, 20]} />
          <meshStandardMaterial color="#ec7a2c" roughness={0.45} />
        </mesh>
      ))}
      <mesh position={[0, 0.17, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.035, 0.035, p * 0.85, 12]} />
        <meshStandardMaterial color="#2fae5a" roughness={0.4} />
      </mesh>
    </group>
  );
};

const PERSONAGEM_POS: [number, number, number] = [-2.0, 0, 0.9];
const VASILHA_POS: [number, number, number] = [-0.95, 0.12, 1.25];
const CARRO_POS: [number, number, number] = [1.3, 0, -0.6];
const CARRO_GIRO = -0.55;

const PLANOS: Plano[] = [
  {t: 0, pos: [-0.4, 2.5, 7.0], alvo: [-2.0, 2.1, 0.9]},
  {t: T.despeja - 0.4, pos: [0.6, 2.6, 6.2], alvo: [-1.3, 1.0, 1.0]},
  {t: T.capo - 0.3, pos: [4.6, 3.4, 4.4], alvo: [1.7, 0.9, -0.1]},
  {t: T.liga - 0.2, pos: [3.6, 2.8, 8.2], alvo: [0.8, 0.9, -0.3]},
  {t: T.pula - 0.3, pos: [0.2, 2.5, 10.4], alvo: [-1.4, 1.9, 0.6]},
];

/** O 3D da vitrine no segundo `s` (usado no modo rápido e no Blender). */
export const quadro3D = (s: number): Quadro3D => {
  const cam: Camera = cameraEm(PLANOS, s, 0.9);
  // atuação: cansado e suado → nega → despeja → olha o carro → pula
  const cansado = 1 - desde(s, T.despeja, 0.6, suave);
  const k = desde(s, T.despeja + 0.3, 0.5, suave) * (1 - desde(s, T.capo - 0.4, 0.4, suave));
  const pulo = pular(s, T.pula, 2);
  const pose = juntar(POSE.parado, desanimar(cansado * 0.8), negar(s, T.negar, 1.3), despejar(k), s > T.pula ? pulo.pose : {});
  const expressao: Expressao = s < T.negar ? 'cansado' : s < T.despeja ? 'triste' : s < T.liga ? 'pensativo' : s < T.pula ? 'surpreso' : 'orgulhoso';
  // carro: capô abre, motor desce e encaixa, capô fecha, liga tremendo
  const capo = desde(s, T.capo, 0.5, suave) * (1 - desde(s, T.fecha, 0.4, suave));
  const motorPos = encaixar(s, T.encaixa, 0.9, [0, 2.6, 0], [0, 0, 0]);
  const treme = tremer(s, T.liga, T.liga + 1.2, 0.035);
  const ligado = s >= T.liga;
  // o jato sai da ponta do bico do galão que está na mão (acompanha braço, inclinação e pulo)
  // a alça do galão fica na palma da mão
  const naMaoOffset: [number, number, number] = [-ALCA_GALAO[0], -0.06 - ALCA_GALAO[1], -ALCA_GALAO[2]];
  const bico = bicoDoGalao(k * 1.35);
  const bocaGalao = pontoNaMao({position: [PERSONAGEM_POS[0], PERSONAGEM_POS[1] + pulo.y, PERSONAGEM_POS[2]], rotation: [0, 0.55, 0], pose}, [naMaoOffset[0] + bico[0], naMaoOffset[1] + bico[1], naMaoOffset[2] + bico[2]]);
  const fundoVasilha: [number, number, number] = [VASILHA_POS[0], VASILHA_POS[1] + 0.05, VASILHA_POS[2]];
  return {
    camera: cam,
    fundo: '#3d424b',
    luz: 1.3,
    cena: (
      <>
        <Garagem />
        <group position={[0, pulo.y, 0]}>
          <Personagem
            {...PERSONAGEM_KIRMASK}
            position={PERSONAGEM_POS}
            rotation={[0, 0.55, 0]}
            pose={pose}
            expressao={expressao}
            suor={cansado}
            tempo={s}
            naMao={s >= T.despeja - 0.2 && s < T.capo ? <group position={naMaoOffset}><Galao inclina={k * 1.35} /></group> : null}
          />
        </group>
        <group position={VASILHA_POS}>
          <Vasilha liquido={desde(s, T.despeja + 0.6, 1.2)} />
        </group>
        {k > 0.6 ? <JatoLiquido s={s} de={bocaGalao} ate={fundoVasilha} /> : null}
        <group position={[CARRO_POS[0] + treme[0], CARRO_POS[1] + treme[1], CARRO_POS[2] + treme[2]]} rotation={[0, CARRO_GIRO, 0]}>
          <CarroDetalhado capo={capo} faroisAcesos={ligado} motor={s >= T.encaixa ? <group position={motorPos}><MotorMini /></group> : null} />
          {ligado ? (
            <group position={[-1.75, 0.3, 0.45]}>
              <Fumaca s={s} forca={0.6} cor="#c9c9cf" />
            </group>
          ) : null}
        </group>
      </>
    ),
  };
};
