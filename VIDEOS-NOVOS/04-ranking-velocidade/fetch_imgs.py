# baixa candidatos do Wikimedia Commons (3 por animal) -> img/raw/<chave>_<n>.jpg + img/creditos.json
import json, sys, time, urllib.request, urllib.parse, urllib.error
from pathlib import Path
P = Path(__file__).parent
Q = {
    "lesma": "garden snail Cornu aspersum",
    "tartaruga": "Aldabra giant tortoise",
    "homem": "man running jogging side view",
    "gato": "domestic cat running",
    "antilope": "pronghorn running",
    "guepardo": "cheetah running",
    "falcao": "peregrine falcon flight",
}
UA = {"User-Agent": "TesteEstilos/1.0 (contato local; video de teste)"}
def get(url):
    for i in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (i + 1))
    raise RuntimeError("429 " + url)
cf = P / "img" / "creditos.json"
cred = json.load(open(cf, encoding="utf-8")) if cf.exists() else {}
for k, q in [(k, Q[k]) for k in (sys.argv[1:] or Q)]:
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=12&gsrsearch="
           + urllib.parse.quote(q + " filetype:bitmap") + "&prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=900")
    d = json.loads(get(api))
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    n = 0
    for p in pages:
        ii = p["imageinfo"][0]
        if ii.get("width", 0) < 800 or not p["title"].lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        f = P / "img" / "raw" / f"{k}_{n}.jpg"
        try:
            if not f.exists(): f.write_bytes(get(ii["thumburl"])); time.sleep(4)
        except Exception as e:
            print("erro", k, e); continue
        md = ii.get("extmetadata", {})
        cred[f"{k}_{n}"] = {"file": p["title"], "url": ii["descriptionurl"],
                             "autor": md.get("Artist", {}).get("value", "")[:200], "licenca": md.get("LicenseShortName", {}).get("value", "")}
        n += 1; time.sleep(4)
        if n >= 2: break
    print(k, n)
    json.dump(cred, open(cf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cred, open(P / "img" / "creditos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
