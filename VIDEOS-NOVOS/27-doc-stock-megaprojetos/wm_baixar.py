import json,urllib.request,time,os
UA={"User-Agent":"estilos-novos-27/1.0 (contato.local)"}
idx={}
for l in open("raw/wm.json",encoding="utf-8"):
    l=l.strip()
    for part in l.replace("}{","}\n{").splitlines():
        if part: idx.update(json.loads(part))
sel={"jz":"File:JetZero blended","x48sky":"File:A pristine blue sky backdrops the X-48B","x48c":"File:X-48C Hybrid - Blended Wing Body Demonstrator (ED13-0056","x48f":"File:X-48B Blended Wing Body aircraft during test flight (1)","b737":"File:Alaska Airlines 737 MAX 9","delta":"File:Delta Boeing 737-900ER N884DN departing Boston February 2025.jpg","usaf":"File:C-17 aircraft over over"}
cred={}
if os.path.exists("img/creditos.json"): cred=json.load(open("img/creditos.json",encoding="utf-8"))
for k,pre in sel.items():
    t=[x for x in idx if x.startswith(pre)][0]; h=idx[t]; out=f"img/{k}.jpg"
    if not os.path.exists(out):
        for i in range(4):
            try: data=urllib.request.urlopen(urllib.request.Request(h["thumb"],headers=UA),timeout=90).read(); break
            except Exception as e: print("retry",k,str(e)[:50]); time.sleep(20)
        open(out,"wb").write(data); time.sleep(1.5)
    cred[k]={"fonte":"Wikimedia Commons","arquivo":t,"licenca":h["lic"],"pagina":h["page"]}; print(k,h["lic"],os.path.getsize(out)//1024,"KB")
json.dump(cred,open("img/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
