import type React from 'react';
import type {Camera} from './camera';

/** O 3D de um vídeo num segundo `s`: câmera, cor de fundo, força da luz e as peças. */
export type Quadro3D = {camera: Camera; fundo: string; luz?: number; cena: React.ReactNode};
