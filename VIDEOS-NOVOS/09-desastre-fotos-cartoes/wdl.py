import urllib.request, urllib.parse, json, time, os, sys
UA = {"User-Agent": "EstilosNovos09/1.0 (teste local; contato local)"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
L = {
 "estadio1991": "File:Hillsborough Stadium in 1991 - geograph.org.uk - 2807213.jpg",
 "ponte_leppings": "File:Hillsborough - Leppings Lane bridge - geograph.org.uk - 2214293.jpg",
 "arquibancada": "File:Hillsborough-North-West-Terrace.jpg",
 "memorial96": "File:\"In Memory of the 96\", Hillsborough - geograph.org.uk - 5958101.jpg",
 "memorial_sheff": "File:Hillsborough Disaster Memorial - 1, Hillsborough, Sheffield - geograph.org.uk - 1254629.jpg",
 "memorial_anfield": "File:Hillsborough Memorial.jpg",
 "mural": "File:Mural in Leppings Lane - geograph.org.uk - 5958093.jpg",
 "justica": "File:Hillsborough Justice Campaign office, Liverpool.jpg",
 "policia_hq": "File:Sheffield, South Yorkshire Police HQ - geograph.org.uk - 796515.jpg",
 "estadio_hoje": "File:Sheffield wednesday hillsborough stadium.jpg",
 "estadio_2024": "File:Hillsborough stadium, 8th March 2024.jpg",
 "assentos": "File:All Seater Stadium^ - geograph.org.uk - 4941974.jpg",
 "rel_painel": "File:The report of the Hillsborough Independent Panel - September 2012.pdf",
 "rel_taylor": "File:Hillsborough Taylor Interim Report Cm765.pdf",
}
def get(u):
    for t in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except Exception as e:
            print("retry", str(e)[:50]); time.sleep(30)
    print("falhou", u[:80]); return None
cp = os.path.join(OUT, "creditos.json"); cred = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
for k, t in L.items():
    dst = os.path.join(OUT, k + ".jpg")
    if os.path.exists(dst): continue
    u = "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=600&titles=" + urllib.parse.quote(t)
    d = json.loads(get(u)); time.sleep(1.5)
    p = list(d["query"]["pages"].values())[0]; ii = p["imageinfo"][0]
    md = ii.get("extmetadata", {})
    cred[k] = {"arquivo": t, "url": ii.get("descriptionurl"), "autor": md.get("Artist", {}).get("value", "")[:120], "licenca": md.get("LicenseShortName", {}).get("value", "")}
    b = get(ii["thumburl"].split("?")[0]); time.sleep(3)
    if not b: continue
    open(dst, "wb").write(b)
    print("ok", k); json.dump(cred, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cred, open(os.path.join(OUT, "creditos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
