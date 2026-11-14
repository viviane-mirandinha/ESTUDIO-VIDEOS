import re,json
t=open('template_src.html',encoding='utf-8').read()
t=re.sub(r"@font-face\{[^\n]*\n",'',t)
t=re.sub(r'const LB=\[.*?\];\n',"""const EDIT=__EDIT__;const ED=Object.fromEntries(EDIT.items.map(i=>[i.id,i]));
const tx=i=>i.type==='text'&&!i.hidden;
const LB=EDIT.items.filter(i=>tx(i)&&i.props.lon!==undefined).map(i=>[i.props.text,i.props.lon,i.props.lat,i.start,i.start+i.dur,i.props.cls]);
""",t,flags=re.S)
t=re.sub(r'const SC=\[.*?\];\n',"const SC=EDIT.items.filter(i=>tx(i)&&i.props.x!==undefined).map(i=>[i.props.text,i.props.x,i.props.y,i.start,i.start+i.dur,i.props.cls]);\n",t,flags=re.S)
t=re.sub(r'const CAM=\[.*?\]\];\n',"const CAM=ED.camera.props.value;\n",t,flags=re.S)
# title + html blocks timing from edit
t=t.replace("const lands={};","""(()=>{const T=ED.titulo;let h=T.props.text;(T.props.highlight||[]).forEach(w=>h=h.replace(w,'<b>'+w+'</b>'));
 $('ttl').innerHTML=h.replace(' É ','<br>É ');$('ttl').dataset.in=T.start;$('ttl').dataset.out=T.hidden?-9:T.start+T.dur;
 ['frc','usa','locks','ships','gauge','cta'].forEach(id=>{const I=ED[id];if(!I)return;$(id).dataset.in=I.hidden?-9:I.start;$(id).dataset.out=I.hidden?-9:I.start+I.dur;});})();
const lands={};""")
t=t.replace('</svg>\n<div id="labels"></div>','</svg>\n<div id="labels"></div>\n<!--__ITEMS__-->',1)
t=t.replace('</body></html>','<!--__ITEMS_SCRIPT__-->\n</body></html>')
P=json.load(open('map_paths.json',encoding='utf-8'))
t=t.replace('__PATHS__',''.join(f'<path id="c-{p["id"]}" class="land" d="{p["d"]}"/>' for p in P))
open('template.html','w',encoding='utf-8').write(t)
print(t.count('__EDIT__'),t.count('CAM=ED'),t.count('ITEMS'))
