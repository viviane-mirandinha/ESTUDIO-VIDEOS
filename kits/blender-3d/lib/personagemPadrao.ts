import type {Acessorios, Barba, Cabelo, Cores, Estilo, Roupa} from './Personagem';

/**
 * O personagem padrão do Kit cotidiano.explicado (aprovado em 29/10/2026): o próprio
 * cotidiano.explicado em versão de vinil. Para usar outro personagem, copie este objeto,
 * mude o que quiser e passe para <Personagem {...SEU_PERSONAGEM} />.
 */
export const PERSONAGEM_KIRMASK: {
  estilo: Estilo;
  roupa: Roupa;
  cabelo: Cabelo;
  barba: Barba;
  acessorios: Acessorios;
  cores: Partial<Cores>;
} = {
  estilo: 'vinil',
  roupa: 'varsity',
  cabelo: 'mullet',
  barba: 'cavanhaque',
  acessorios: {brinco: true, tatuagem: true, bolsa: true, bolsosCargo: true, cadarcos: true},
  cores: {pele: '#e8bb96', roupa: '#f1ead9', baixo: '#ffffff', calca: '#1d1d22', tenis: '#18181c', sola: '#d9d6cf', cabelo: '#1a120e'},
};
