import sys,os,json,shutil,subprocess,datetime
p=sys.argv[1];nn=int(sys.argv[2]);inicio=sys.argv[3];obs=sys.argv[4];fraco=sys.argv[5]
ed=json.load(open(os.path.join(p,"edit.json"),encoding="utf-8"))
out=os.path.join(p,ed["name"]+".mp4");shutil.copy2(os.path.join(p,"final.mp4"),out)
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out],capture_output=True,text=True).stdout)
subprocess.run(["ffmpeg","-v","error","-y","-i",out,"-vf",f"fps=12/{dur:.2f},scale=200:-1,tile=6x2","-frames:v","1",os.path.join(p,"sheet.jpg")])
fim=datetime.datetime.now().astimezone();ini=datetime.datetime.fromisoformat(inicio)
rs=int(open(os.path.join(p,"render_segundos.txt")).read().strip())
rel={"video":nn,"estilo":ed["estilo"],"inicio":ini.isoformat(timespec="seconds"),"fim":fim.isoformat(timespec="seconds"),
 "minutos":round((fim-ini).total_seconds()/60,1),"render_segundos":rs,"voz":"usuario","observacoes":obs,"ponto_fraco":fraco}
open(os.path.join(p,"RELATORIO.json"),"w",encoding="utf-8").write(json.dumps(rel,ensure_ascii=False,indent=1))
print(out,round(dur,2))
