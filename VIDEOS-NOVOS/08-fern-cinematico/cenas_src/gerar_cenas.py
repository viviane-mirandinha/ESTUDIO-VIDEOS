import pathlib
here = pathlib.Path(__file__).parent
lib = (here / "_fern_lib.js").read_text(encoding="utf-8")
dst = pathlib.Path(str(__import__("pathlib").Path(__file__).resolve().parents[3] / "editor" / "templates" / "scenes"))
for f in sorted(here.glob("fern_*.html")):
    (dst / f.name).write_text(f.read_text(encoding="utf-8").replace("/*FERNLIB*/", lib), encoding="utf-8")
    print(f.name)
