import urllib.request,urllib.parse,json,os,time,sys
KEY=__import__("os").environ.get("KEY", "")
UA={"User-Agent":"EstudioTeste/1.0 (contato local; video educativo)"}
D=os.path.dirname(os.path.abspath(__file__)); IMG=os.path.join(D,"img","cand"); CL=os.path.join(D,"clips","cand")
os.makedirs(IMG,exist_ok=True); os.makedirs(CL,exist_ok=True)
def get(u,tries=3):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read()
        except Exception as e: print("retry",str(e)[:80],flush=True); time.sleep(15)
    return None
cred={}
WIKI=[("burj","Burj Khalifa"),("marmuerto","Dead Sea shore"),("dryvalley","McMurdo Dry Valleys"),("curiosity","Curiosity rover Mars selfie"),
("denman","Denman Glacier"),("twinotter","Twin Otter Antarctica"),("gondwana","Gondwana map"),("glossopteris","Glossopteris fossil"),
("europa","Europa moon Galileo"),("vostokst","Vostok Station"),("wissard","WISSARD drill"),("bloodfalls","Blood Falls Taylor Glacier"),
("erebuslava","Erebus lava lake"),("erebus","Mount Erebus"),("icecave","Erebus ice cave"),("putorana","Putorana Plateau"),("tratado","Antarctic Treaty 1959 signing"),
("thwaites","Thwaites Glacier"),("alh84001","ALH84001"),("meteorito","meteorite Antarctica ice"),("icecore","ice core Antarctica"),
("michigan","Lake Michigan satellite"),("radargram","ice penetrating radar echogram"),("anfipodo","amphipod Antarctic"),("esponja","Antarctic sponge seabed"),
("bluemarble","Blue Marble 2002 land surface ocean ice cloud"),("rift","West Antarctic Rift"),("weddell","Weddell Sea ice"),("polarstern","icebreaker Antarctica"),
("campo","Antarctica field camp tents"),("plateau","Antarctic plateau snow"),("gravedad","Wilkes Land crater gravity"),("deadseasign","Dead Sea lowest point sign"),
("selva","temperate rainforest Valdivian"),("sahara","Sahara dunes"),("alpes","Alps peaks aerial"),("bandera","Flag of the Antarctic Treaty"),("kerosene","Vostok borehole drilling")]
for key,q in WIKI:
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":3,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1600})
    b=get(u); time.sleep(1.5)
    if not b: continue
    pages=sorted(json.loads(b).get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",0))
    for k,p in enumerate(pages):
        ii=p["imageinfo"][0]; fn=f"w_{key}_{k}.jpg"; fp=os.path.join(IMG,fn)
        if not os.path.exists(fp):
            bb=get(ii.get("thumburl") or ii["url"]); time.sleep(1.5)
            if not bb: continue
            open(fp,"wb").write(bb)
        md=ii.get("extmetadata",{}); cred[fn]={"title":p["title"],"artist":md.get("Artist",{}).get("value","")[:120],"license":md.get("LicenseShortName",{}).get("value","")}
    print("wiki",key,len(pages),flush=True)
    json.dump(cred,open(os.path.join(IMG,"creditos.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
VID=[("vant","antarctica aerial"),("viceberg","iceberg"),("vglaciar","glacier aerial"),("vshelf","ice shelf"),("vavion","airplane flying over snow"),
("vbarco","icebreaker"),("vnieve","snow wind blizzard"),("vsahara","sahara desert"),("vmontana","snowy mountains aerial"),("vselva","rainforest aerial"),
("vlava","lava"),("vvolcan","volcano smoke"),("vsat","satellite earth orbit"),("vmeteoro","meteor"),("vagua","underwater dark"),("vkrill","krill"),
("vcueva","ice cave"),("vderrite","melting ice"),("vgrieta","ice crevasse"),("vpetroleo","oil rig"),("vmar","ocean waves aerial"),("vtierra","earth from space")]
for k,q in VID:
    b=get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true"}))
    if not b: continue
    hits=json.loads(b).get("hits",[])
    for i,h in enumerate(hits[:3]):
        v=h["videos"]; f=v.get("medium") or v.get("small")
        if not f or not f.get("url"): continue
        fp=os.path.join(CL,f"{k}{i}.mp4")
        if not os.path.exists(fp):
            bb=get(f["url"])
            if bb: open(fp,"wb").write(bb)
    print("pix",k,len(hits),flush=True)
print("FIM")
