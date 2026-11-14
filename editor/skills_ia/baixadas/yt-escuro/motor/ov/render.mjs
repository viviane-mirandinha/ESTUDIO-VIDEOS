// node render.mjs <planjs> <outdir> [workers] [idx,idx..]
import {chromium} from 'playwright-core';
import fs from 'node:fs'; import path from 'node:path'; import {spawnSync} from 'node:child_process'; import {pathToFileURL, fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const [planjs, outdir, W = '6', only] = process.argv.slice(2);
fs.copyFileSync(planjs, path.join(here, 'plan.js'));
const PLAN = new Function(fs.readFileSync(planjs, 'utf8') + ';return PLAN;')();
fs.mkdirSync(outdir, {recursive: true});
const EXE = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe'].find((b) => fs.existsSync(b));
const browser = await chromium.launch({executablePath: EXE, args: ['--force-color-profile=srgb', '--hide-scrollbars', '--disable-lcd-text', '--font-render-hinting=none']});
let todo = PLAN.map((_, i) => i); if (only) todo = only.split(',').map(Number);
todo = todo.filter((i) => !fs.existsSync(path.join(outdir, `ins_${String(i).padStart(3, '0')}.mov`)) || only);
async function work() {
  const page = await browser.newPage({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
  page.on('pageerror', (e) => console.error('PAGEERROR', e.message));
  while (todo.length) {
    const i = todo.shift(); const it = PLAN[i]; const id = String(i).padStart(3, '0');
    const fd = path.join(outdir, 'fr_' + id); fs.rmSync(fd, {recursive: true, force: true}); fs.mkdirSync(fd);
    await page.goto(pathToFileURL(path.join(here, 'index.html')).href + '?i=' + i);
    await page.waitForFunction(() => window.ready); await page.evaluate(() => window.ready);
    const N = Math.round(it.dur * 30);
    for (let f = 0; f < N; f++) {
      await page.evaluate((t) => window.seek(t), f / 30);
      await page.screenshot({path: path.join(fd, String(f).padStart(5, '0') + '.png'), omitBackground: true});
    }
    const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '30', '-i', path.join(fd, '%05d.png'), '-c:v', 'qtrle', '-pix_fmt', 'argb', path.join(outdir, `ins_${id}.mov`)]);
    if (r.status) console.error(String(r.stderr)); else fs.rmSync(fd, {recursive: true, force: true});
    console.log('ok', i, it.type, N);
  }
  await page.close();
}
await Promise.all(Array.from({length: +W}, work));
await browser.close();
