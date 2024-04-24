from Modele_db.modele_db import ZAM_PIANKI, RAPORT_KJ_DO_DOSTAWY_PIANEK as kj, KOMPLETY_PIANEK, session
from sqlalchemy import select, text
import json 
import os


# with open("linki.json", "r", encoding="UTF8") as f:
    # rysunki_dir = json.load(f)["rysunki_dokumentacja"]
rysunki_dir = "Flask_server/Bluprints/wydzial_pianek/static/RYSUNKI/"

def raport_jakosciowy_dane(id):
    bryla_jakosc = select(ZAM_PIANKI.kod ,ZAM_PIANKI.model, ZAM_PIANKI.nr_kompletacji, ZAM_PIANKI.opis, ZAM_PIANKI.ile_zam, ZAM_PIANKI.zam1, ZAM_PIANKI.zam2).where(
                ZAM_PIANKI.lp == id)

    kod, model, nr_kompletacji, opis, ile_zam, zam1, zam2 = session.execute(bryla_jakosc).first()
    bryla_gen = session.execute(select(
                                        KOMPLETY_PIANEK.kod, KOMPLETY_PIANEK.bryla_gen).where(KOMPLETY_PIANEK.kod == kod)).first()[1]

    tabelka_kj = [list(x) for x in session.execute(text(f"SELECT TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where MODEL = '{model}' and BRYLA = '{bryla_gen}'")).fetchall()]


    uw = [list(x) for x in session.execute(select(kj.nr_pianki, kj.uwaga_wysokosc, kj.data_dodania).where(kj.model == model, kj.bryla_gen == bryla_gen, kj.blad_dopuszczalny_wysokosc==True, kj.uwaga_wysokosc != "")).all()]
    us = [list(x) for x in session.execute(select(kj.nr_pianki, kj.uwaga_szerokosc, kj.data_dodania).where(kj.model == model, kj.bryla_gen == bryla_gen, kj.blad_dopuszczalny_szerokosc==True, kj.uwaga_szerokosc != "")).all()]
    ud = [list(x) for x in session.execute(select(kj.nr_pianki, kj.uwaga_dlugosc, kj.data_dodania).where(kj.model == model, kj.bryla_gen == bryla_gen, kj.blad_dopuszczalny_dlugosc==True, kj.uwaga_dlugosc != "")).all()]
    print(len(uw), len(us), len(ud))

    for r in tabelka_kj:

        gif_dir = rysunki_dir + r[4][0] + "/"
        # gif_dir = "/" + r[4][0] + "/"
        # gif_dir = r[4][0] + "/"

        try:
            gif_dir = "/" + r[4][0] + "/"+[x for x in os.listdir(gif_dir) if r[4] in x][0]
        except:
            gif_dir = "BRAK"

        r.append(gif_dir)
        r.append("")
        r.append("")
        r.append("")
                

    for r in tabelka_kj:
        for d in ud:
            if r[4] == d[0]:
                r[-2] = "d" + d[1]
                
        for s in us:
            if r[4] == s[0]:
                r[-1] = "s" + s[1]


        for w in uw:
            if r[4] == w[0]:
                r[-3] = "w"+w[1]
    
    return model, bryla_gen, opis, ile_zam, tabelka_kj