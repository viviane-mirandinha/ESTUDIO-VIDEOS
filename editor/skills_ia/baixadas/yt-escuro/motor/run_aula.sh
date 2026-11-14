#!/bin/bash
# uso: bash run_aula.sh N "TITULO"
cd "$(dirname "$0")"
n=$1; k=a$n
python -I make_base.py $k > $k/run.log 2>&1 || { echo ERRO base >> $k/run.log; exit 1; }
python -I build.py $k >> $k/run.log 2>&1
(cd ov && node render.mjs plan_$k.js ../$k/ins 8 >> ../$k/render.log 2>&1)
PYTHONIOENCODING=utf-8 python -I compose.py $k "../0$n - 07-11-2026 - BRECHA VIRAL - $2.mp4" >> $k/run.log 2>&1 && echo FIM >> $k/run.log
