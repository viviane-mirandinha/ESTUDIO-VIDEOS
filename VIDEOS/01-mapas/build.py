# Projeto no formato do editor local. template.html = composicao (mapa embutido). Tudo editavel em edit.json.
# Regerar mapa: template_src.html + map_paths.json (gen_map) -> /tmp/patch.py. Render: build_from_edit.py <pasta> --render
import subprocess,sys,os
subprocess.run([sys.executable,os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "editor", "build_from_edit.py"),os.path.dirname(os.path.abspath(__file__))]+sys.argv[1:])
