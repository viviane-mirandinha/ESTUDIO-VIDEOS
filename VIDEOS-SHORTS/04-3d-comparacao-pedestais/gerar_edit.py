import os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "_template-palco3d"))
from palco import Projeto

ROT = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "ROTEIROS-SHORTS" / "04 - 3D COMPARACAO PEDESTAIS - Quantas horas de trabalho custa um iPhone.txt")
NAME = "04 - 3D COMPARACAO PEDESTAIS - Quantas horas de trabalho custa um iPhone"
P = Projeto(D, ROT)
at, end = P.at, P.end
DUR = round(P.voz_dur + 0.6, 2)

P.param("breadcrumb", "HORAS DE TRABALHO · BRASIL × EUA", "Breadcrumb (topo)")
P.param("cor_br", "#E3C595", "Cor pedestal Brasil")
P.param("cor_us", "#A493E6", "Cor pedestal EUA")

WIDE = ([0, 3.4, 21.0], [0, 1.9, 0])
CBR = ([-1.6, 2.5, 13.0], [-1.6, 1.0, 0])
CUS = ([1.6, 2.5, 13.0], [1.6, 1.0, 0])
CUSB = ([1.2, 2.3, 10.5], [1.2, 0.85, 0])

# tempos-chave (todos da fala)
T_CONTA, T_PRECOS, T_BIG, T_ENCHER, T_CARRO = at("Vamos"), at("Agora os preços"), at("Um Big Mac"), at("Encher"), at("E o carro")
T_REPARA, T_LADOB, T_ENTAO, T_EAI = at("E repara"), at("Agora, o lado B"), at("Então o americano"), at("E aí")

# 1) a pergunta
P.chap("A PERGUNTA", 0, T_CONTA)
P.cam("aberto", 0, *WIDE, trans=0)
P.cena("iPhone: 5 meses x 3 semanas", 0, T_CONTA, objeto="iphone", br=21.7, us=3, br_t=at("5 meses") - 0.2, us_t=at("3 semanas") - 0.1)
P.rot("≈ 5 MESES", at("5 meses"), T_CONTA, "branco", anchor="br_top", sub="de trabalho")
P.rot("< 3 SEMANAS", at("3 semanas"), T_CONTA, "pill", anchor="us_top")

# 2) por hora
P.chap("POR HORA", T_CONTA, T_PRECOS)
P.cena("relógios: salário por hora", T_CONTA, T_PRECOS, objeto="relogio", br=7.37, us=7.25, max=18,
       br_t=at("R$ 7,37"), us_t=at("7,25"))
P.stk("EM HORAS DE TRABALHO", at("em horas"), at("No Brasil", 2), "amarelo", y=640, size=64)
P.cam("perto Brasil", at("No Brasil", 2), *CBR)
P.rot("R$ 1.621 / MÊS", at("1.621"), at("R$ 7,37"), "branco", anchor="br_top", sub="salário mínimo")
P.rot("R$ 7,37", at("R$ 7,37"), T_PRECOS, "pill", anchor="br_top", sub="por hora")
P.cam("perto EUA", at("Nos Estados Unidos", 2), *CUS)
P.rot("US$ 7,25", at("7,25"), T_PRECOS, "pill", anchor="us_top", sub="por hora")
P.cam("aberto", at("Quase o mesmo"), *WIDE)
P.stk("REAL ≠ DÓLAR", at("real"), T_PRECOS, "vermelho", y=640)

# 3) iPhone
P.chap("CELULAR", T_PRECOS, T_BIG)
P.cena("iPhone: 1.085 h x 110 h", T_PRECOS, T_BIG, objeto="iphone", br=1085, us=110, br_t=at("1.085"), us_t=at("110"))
P.rot("R$ 7.999", at("R$ 7.999"), at("São cerca"), "branco", anchor="br_top")
P.rot("US$ 799", at("799"), at("São cerca"), "branco", anchor="us_top")
P.rot("≈ 1.085 h", at("1.085"), T_BIG, "branco", anchor="br_top", sub="de trabalho")
P.rot("110 h", at("110"), T_BIG, "pill", anchor="us_top")
P.stk("≈ 10× MAIS", at("10 vezes"), T_BIG, "amarelo", y=640)

# 4) Big Mac
P.chap("LANCHE", T_BIG, T_ENCHER)
P.cena("Big Mac: 3 h x 50 min", T_BIG, T_ENCHER, objeto="burger", br=3.2, us=0.83, br_t=at("mais de 3"), us_t=at("50 minutos"))
P.rot("> 3 HORAS", at("mais de 3"), T_ENCHER, "branco", anchor="br_top")
P.rot("≈ 50 MIN", at("50 minutos"), T_ENCHER, "pill", anchor="us_top")

# 5) gasolina
P.chap("GASOLINA", T_ENCHER, T_CARRO)
P.cena("tanque 50 L: 45 h x 8 h", T_ENCHER, T_CARRO, objeto="bomba", br=45, us=8, br_t=at("umas 45"), us_t=at("umas 8"))
P.stk("TANQUE DE 50 LITROS", at("tanque"), at("umas 45"), "amarelo", y=640, size=64)
P.rot("≈ 45 h", at("umas 45"), T_CARRO, "branco", anchor="br_top")
P.rot("≈ 8 h", at("umas 8"), T_CARRO, "pill", anchor="us_top")
P.stk("GASOLINA LÁ MAIS CARA", at("mesmo com"), T_CARRO, "vermelho", y=640, size=60)

# 6) carro
P.chap("CARRO", T_CARRO, T_REPARA)
P.cena("carro zero: 4 anos x 1,5 ano", T_CARRO, T_REPARA, objeto="carro", br=48, us=18, br_t=at("4 anos"), us_t=at("1 ano e meio"))
P.stk("CARRO 0 KM MAIS BARATO", at("carro zero"), at("4 anos"), "amarelo", y=640, size=60)
P.rot("≈ 4 ANOS", at("4 anos"), T_REPARA, "branco", anchor="br_top", sub="de salário mínimo")
P.rot("≈ 1,5 ANO", at("1 ano e meio"), T_REPARA, "pill", anchor="us_top")

# 7) Califórnia
P.chap("CALIFÓRNIA", T_REPARA, T_LADOB)
P.cena("por hora: EUA 7,25 -> Califórnia 16,90", T_REPARA, T_LADOB, objeto="relogio", br=7.37, us=7.25, us2=16.9, max=18,
       br_t=T_REPARA, us_t=T_REPARA, us2_t=at("16,90"))
P.rot("SALÁRIO MAIS BAIXO DOS EUA", at("isso usando"), at("Na Califórnia"), "branco", x=540, y=600, size=56)
P.rot("R$ 7,37/h", T_REPARA + 0.3, T_LADOB, "branco", anchor="br_top")
P.rot("US$ 7,25/h", T_REPARA + 0.3, at("16,90"), "branco", anchor="us_top")
P.rot("US$ 16,90/h", at("16,90"), T_LADOB, "pill", anchor="us_top", sub="Califórnia")
P.stk("MAIS QUE O DOBRO", at("mais que o dobro"), T_LADOB, "verde", y=600)

# 8) lado B
P.chap("O LADO B", T_LADOB, T_EAI)
P.cam("EUA de perto", T_LADOB, *CUSB)
P.cena("lado B: hospital + faculdade", T_LADOB, T_ENTAO, objeto="ladob", hosp_t=at("pronto-socorro") - 0.3, cap_t=at("Faculdade") - 0.2)
P.stk("O LADO B", at("lado B"), at("não tem SUS"), "vermelho", y=620)
P.rot("SEM SUS", at("SUS"), at("Uma ida"), "vermelho", x=540, y=640)
P.rot("> US$ 1.000", at("mil dólares"), at("Faculdade"), "vermelho", anchor="hosp", sub="pronto-socorro sem plano")
P.rot("FACULDADE CARA", at("Faculdade"), at("a lei"), "vermelho", x=540, y=600)
P.rot("SEM FÉRIAS PAGAS", at("férias"), T_ENTAO, "vermelho", x=540, y=520)
P.rot("SEM 13º", at("décimo"), T_ENTAO, "vermelho", x=540, y=660)
P.cena("resumo EUA", T_ENTAO, T_EAI, objeto="resumo", br=None, us=None)
P.cam("EUA aberto", T_ENTAO, [1.0, 2.9, 11.5], [1.0, 1.45, 0])
P.rot("COMPRA MAIS RÁPIDO", at("compra"), T_EAI, "verde", x=540, y=540)
P.rot("PAGA CARO POR OUTRAS", at("paga caro"), T_EAI, "vermelho", x=540, y=680)

# 9) final
P.chap("E AÍ?", T_EAI, DUR)
P.cam("aberto", T_EAI, *WIDE)
P.cena("final: 5 meses x 3 semanas", T_EAI, DUR + 1, objeto="iphone", br=21.7, us=3, br_t=T_EAI, us_t=T_EAI + 0.2, cresce=0.8)
P.stk("VOCÊ TROCARIA?", at("você trocaria"), DUR, "verde", y=560, size=84)
P.stk("BRASIL OU EUA?", at("Comenta"), DUR, "amarelo", y=720, rot=3)

P.salvar(NAME, "3D comparação pedestais (Brasil × EUA)", {
    "canal": "@minuto_curioso12", "canal_url": "https://www.instagram.com/minuto_curioso12/",
    "video": "https://www.instagram.com/reel/DeolZXGRwBg/",
    "nota": "261 mil views; 3D minimalista, pedestais bege x lilás, pilhas crescendo, pílulas verde-neon, legenda em caixa karaokê"},
    "cena.js", dur=DUR)
