// "Assa" a cena 3D de um vídeo: empacota o código (cena3d.tsx) e grava cena.glb + quadros.json.
//   node bake/assar.mjs <arquivo-da-cena.tsx> <pasta-de-saida> [nome]
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';

const KIT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [cenaArg, saidaArg, nome = 'cena'] = process.argv.slice(2);
if (!cenaArg || !saidaArg) {
  console.error('Uso: node bake/assar.mjs <cena3d.tsx> <pasta-de-saida> [nome]');
  process.exit(1);
}
const cena = path.resolve(cenaArg);
const saida = path.resolve(saidaArg);
const cache = path.join(KIT, 'node_modules', '.cache', 'bake');
fs.mkdirSync(cache, {recursive: true});
const arquivo = path.join(cache, 'assar.mjs');
const modulos = path.join(KIT, 'node_modules');
await build({
  entryPoints: [path.join(KIT, 'bake', 'assar-entrada.tsx')],
  bundle: true,
  platform: 'node',
  format: 'esm',
  jsx: 'automatic',
  outfile: arquivo,
  logLevel: 'error',
  nodePaths: [modulos],
  plugins: [
    {
      name: 'estudio-blender',
      setup(b) {
        b.onResolve({filter: /^__CENA__$/}, () => ({path: cena}));
        b.onResolve({filter: /^@estudio3d$/}, () => ({path: path.join(KIT, 'lib', 'index.ts')}));
        // uma cópia só do three.js e do react para todo mundo (senão as cores se perdem)
        b.onResolve({filter: /^three$/}, () => ({path: path.join(modulos, 'three', 'build', 'three.module.js')}));
        b.onResolve({filter: /^react$/}, () => ({path: path.join(modulos, 'react', 'index.js')}));
      },
    },
  ],
  mainFields: ['module', 'main'],
  conditions: ['import', 'module'],
  banner: {js: "import {createRequire as __cr} from 'module'; const require = __cr(import.meta.url);"},
});
process.stdout.write('Assando a cena… ');
execFileSync(process.execPath, [arquivo, nome, saida], {stdio: 'inherit'});
