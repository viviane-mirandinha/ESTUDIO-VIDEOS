# grava páginas do YouTube SÓ depois que as capas carregaram; o .webm final começa 5 s antes do "pronto"
import sys, asyncio, os, shutil, json, time, subprocess
from playwright.async_api import async_playwright
OUT, JOBS = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
LOADED = """()=>{const ims=[...document.querySelectorAll('ytd-rich-item-renderer img, ytd-video-renderer img, ytd-grid-video-renderer img, yt-thumbnail-view-model img, ytd-thumbnail img')]
 .filter(i=>{const r=i.getBoundingClientRect();return r.width>80&&r.bottom>0&&r.top<1080});
 return [ims.length, ims.filter(i=>i.complete&&i.naturalWidth>0&&i.src&&!i.src.startsWith('data:')).length]}"""
async def ready(pg, tmax=25):
    t0 = time.time()
    while time.time() - t0 < tmax:
        n, ok = await pg.evaluate(LOADED)
        if n >= 3 and ok == n: return True
        await pg.wait_for_timeout(500)
    return False
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        for name, url, mode, secs in JOBS:
            try:
                ctx = await b.new_context(viewport={"width":1920,"height":1080}, locale="en-US", color_scheme="dark",
                    record_video_dir=OUT+"/tmp_"+name, record_video_size={"width":1920,"height":1080})
                await ctx.add_cookies([{"name":"SOCS","value":"CAI","domain":".youtube.com","path":"/"},{"name":"PREF","value":"f6=400&hl=en&gl=US","domain":".youtube.com","path":"/"}])
                T0 = time.time(); pg = await ctx.new_page()
                await pg.goto(url, wait_until="domcontentloaded", timeout=60000); await pg.wait_for_timeout(3000)
                if mode == "popular":
                    loc = pg.get_by_text("Popular", exact=True)
                    if await loc.count(): await loc.first.click(); await pg.wait_for_timeout(2500)
                # pré-carrega: desce devagar pela área que será gravada e volta ao topo
                for _ in range(30): await pg.mouse.wheel(0, 60); await pg.wait_for_timeout(120)
                await ready(pg, 10)
                await pg.evaluate("()=>window.scrollTo(0,0)"); await pg.wait_for_timeout(800)
                ok = await ready(pg, 15)
                tr = time.time() - T0
                for _ in range(secs * 10): await pg.mouse.wheel(0, 6); await pg.wait_for_timeout(100)
                await ctx.close()
                d = OUT+"/tmp_"+name; f = [x for x in os.listdir(d) if x.endswith(".webm")][0]
                ss = max(0, tr - 5)
                subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{ss:.2f}","-i",d+"/"+f,"-c:v","libvpx","-b:v","6M","-an",OUT+"/"+name+".webm"], check=True)
                shutil.rmtree(d, ignore_errors=True); print("ok", name, "capas", ok, "corte", round(ss,1), flush=True)
            except Exception as e: print("ERRO", name, str(e)[:120], flush=True)
        await b.close()
asyncio.run(main())
