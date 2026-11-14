"""Gera template.html = template_src.html + kit inlinado (no marcador /*__KIT__*/)."""
import sys, os
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lowpoly-kit.js")
p = sys.argv[1]
src = open(os.path.join(p, "template_src.html"), encoding="utf-8").read()
open(os.path.join(p, "template.html"), "w", encoding="utf-8").write(src.replace("/*__KIT__*/", open(K, encoding="utf-8").read()))
print("template.html ok")
