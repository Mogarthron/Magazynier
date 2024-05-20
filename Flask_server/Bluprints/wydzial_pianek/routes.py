from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session, ZAM_PIANKI, RAPORT_KJ_DO_DOSTAWY_PIANEK, AKTYWNE_DOSTAWY 
from Modele_db import engine
from sqlalchemy import or_, text

from Pianki.Dostawy_pianek import obietosci_samochodow, wykers_zapelnienia_samochodow
import plotly.express as px
import plotly

from ..wydzial_pianek import wydzial_pianek
from ..wydzial_pianek.funkcje_pomocnicze import *

import pandas as pd

@wydzial_pianek.route("/")
def index():   


    return render_template("wydzial_pianek.html", title="Wydział pianek")

@wydzial_pianek.route("/naklejki")
def naklejki():

    with engine.begin() as conn:
        zp = conn.execute(text(f"""SELECT MODEL, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE,
                        NR_PARTII from ZAM_PIANKI WHERE ZAM1 in('24/0486') --AND OPIS NOT LIKE '%AVANT%'"""))
    
    zam_pianki = zp.fetchall()

    wiersze = list()

    for row in zam_pianki:
        
        for i in range(row[3]):
            
            wiersze.append([row[4], row[1], f"{i+1}/{row[3]}", row[0], row[2].replace(row[0], "").strip()])
          

    return render_template("naklejki_na_paczki_pianek_zebra.html", wiersze=wiersze)

@wydzial_pianek.route("/dostawy_pianek")
def dostawy_pianek():

    akt_dos = session.query(AKTYWNE_DOSTAWY.nr_zam, AKTYWNE_DOSTAWY.dostawca, AKTYWNE_DOSTAWY.data_zamowienia, AKTYWNE_DOSTAWY.preferowana_data_dostawy).filter(AKTYWNE_DOSTAWY.aktywna != 11).all()

    tabelka_dostawy_pianek = [
        #Data zamó[wienia], oczekiwnie na potwierdzenie, data potwierdzenia, data dostawy, nr_partii, nr_samochodu, status, obietosc
        ["2024-04-05", "", "", "2024-05-10", "13/01, 14/01", "PIANPOL 10_24", "DOSTARCZONY CAŁKOWICIE"],
        ["2024-03-27", "", "", "2024-05-17", "13/01", "VITA 8_24", "DOSTARCZONY CAŁKOWICIE"],
        ["2024-05-08", "", "", "2024-06-07", "19/01", "PIANPOL 11_24", "NIE POTWIERDZONY"],
        ["2024-05-08", "", "", "2024-06-07", "19/02", "PIANPOL 12_24", "NIE POTWIERDZONY"],
        ["2024-05-17", "", "", "2024-06-21", "20/02", "PIANPOL 13_24", "NIE POTWIERDZONY"],
    ]

    zp_tab = []
    for i in tabelka_dostawy_pianek:
        with engine.begin() as conn:
                
            _zp_tab = conn.execute(text(f"""SELECT LP, TYDZIEN, KOD, MODEL, NR_KOMPLETACJI, OPIS,
                                                ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY, GALANTERIA, SIEDZISKA_HR,
                                                LENIWA, ZAM1, ZAM2, UWAGI, POTW_DATA_DOS_1, POTW_DATA_DOS_2,
                                                nr_SAMOCHODU, nr_PARTII 
                                        FROM ZAM_PIANKI WHERE NR_SAMOCHODU LIKE '%{i[-2]}%' AND NR_PARTII IS NOT NULL""")).all()
            
        zp_tab += _zp_tab

    zp_tab = pd.DataFrame(zp_tab, columns="LP,TYDZIEN,KOD,MODEL,NR_KOMPLETACJI,OPIS,ILE_ZAMOWIONE,ZNACZNIK_DOSTAWCY,GALANTERIA,SIEDZISKA_HR,LENIWA,ZAM1,ZAM2,UWAGI,POTW_DATA_DOS_1,POTW_DATA_DOS_2,nr_SAMOCHODU,nr_PARTII".split(",")) 

    zp_tab["KOMPLETACJA"] = zp_tab["MODEL"] + " " + zp_tab["NR_KOMPLETACJI"]
    zp_tab["nr_SAMOCHODU"].fillna("", inplace=True)
    zp_tab.drop_duplicates(inplace=True)

    

    df = pd.concat([
            obietosci_samochodow(x, zp_tab).groupby(
                ["SAMOCHOD", "KOMPLETACJA"]).sum()[
                    ["OBJ","GAL_OBJ","SHR_OBJ","LEN_OBJ"]].reset_index() for x in {x[1] for x in akt_dos}    
        ]
        ).sort_values(by="SAMOCHOD").reset_index(drop=True)
   
    fig = wykers_zapelnienia_samochodow(df)
    

    for t in tabelka_dostawy_pianek: 
        t.append(f"{df[df.SAMOCHOD == t[-2]].OBJ.sum():.0f}") 
    
    
    return render_template("dostawy_pianek.html", title="Dostawy pianek", 
                                                  tabelka_dostawy_pianek=tabelka_dostawy_pianek,  
                                                  graphJSON=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


@wydzial_pianek.route("/przyjecie_dostawy/<nr_samochodu>", methods=["GET", "POST"])
def przyjecie_dostawy(nr_samochodu):
    
    pianki_w_drodze = session.query(ZAM_PIANKI).filter(ZAM_PIANKI.nr_samochodu.like(f"%{nr_samochodu}%")).all()
    
    json_pianki_w_drodze = list(map(lambda x: x.pianki_w_drodze_to_json(), pianki_w_drodze))
    
    raport_realizacji_dostawy = [
        ["ADAM RZEPKO", 57, 190, 0, 0, 0],
        ["PIOTR ŁUPIŃSKI", 57, 0, 0, 305, 225],
        ["PAWEŁ MIŚKO", 57, 0, 0, 165, 225],
    ]

    if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
        # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
        return redirect(url_for("wydzial_pianek.raport_jakosciowy", nr_samochodu=nr_samochodu ,id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("przyjecie_dostawy.html", title=f"Przyjecie dostawy {nr_samochodu}", 
                                                        nr_samochodu=nr_samochodu, 
                                                        raport_realizacji_dostawy=raport_realizacji_dostawy,
                                                        pianki_w_drodze={"pianki_w_drodze":json_pianki_w_drodze})



@wydzial_pianek.route("/raport_jakosciowy/", defaults={"id": None, "nr_samochodu": None})
@wydzial_pianek.route("/raport_jakosciowy/<nr_samochodu>/<id>", methods=["GET", "POST"])
def raport_jakosciowy(nr_samochodu, id):
    
    if id:
               
        model, bryla_gen, opis, ile_zam, tabelka_kj = raport_jakosciowy_dane(id)

        #['uwagiDlugosc', 'bladAkceptowanyDlugosc', 'uwagiSzerokosc', 'bladAkceptowanySzerokosc', 'uwagiWysokosc', 'bladAkceptowanyWysokosc', 'uwagiInne', 'pozycjaDoReklamacji', 'numerPaczki_1']
        if request.method == "POST":
            
            numery_z_formy = list(request.form.keys())[-1].split("_")
            nr_paczki = numery_z_formy[1]
            nr_pianki = numery_z_formy[3]
            blad_dopuszczalny_wysokosc = 1 if type(request.form.get("bladAkceptowanyWysokosc")) == str else 0 
            blad_dopuszczalny_szerokosc = 1 if type(request.form.get("bladAkceptowanySzerokosc")) == str else 0 
            blad_dopuszczalny_dlugosc = 1 if type(request.form.get("bladAkceptowanyDlugosc")) == str else 0 
            blad_dopuszczalny = 1 if type(request.form.get("pozycjaDoReklamacji")) == str else 0 
            
            session.add(RAPORT_KJ_DO_DOSTAWY_PIANEK(id, nr_paczki, model, bryla_gen, nr_pianki, 
                                                    blad_dopuszczalny_wysokosc, request.form["uwagiWysokosc"], 
                                                    blad_dopuszczalny_szerokosc, request.form["uwagiSzerokosc"],
                                                    blad_dopuszczalny_dlugosc, request.form["uwagiDlugosc"], 
                                                    blad_dopuszczalny, request.form["uwagiInne"]))

            session.commit()

        # print(opis)
        # print(pd.DataFrame(tabelka_kj))
        return render_template("raport_jakosciowy.html", opis=opis, ile_zam=ile_zam, tabelka_kj=tabelka_kj, nr_samochodu=nr_samochodu)
    
    else:
        
        kj = RAPORT_KJ_DO_DOSTAWY_PIANEK
               
        res = session.query(kj)   

        json_kj = list(map(lambda x: x.kj_to_json(), res))
        return json_kj
    

@wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
def plan_pracy():

    plan_pracy = session.query(ZAM_PIANKI).filter(
                    or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
    
    json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))


    if request.method == "POST" and "zakonczono" in list(request.form.keys())[0]:
        print("zakonczono id", int(list(request.form.keys())[0].replace("zakonczono_", "")))
        
    if request.method == "POST" and "edytuj" in list(request.form.keys())[0]:
        print("edytuj id", int(list(request.form.keys())[0].replace("edytuj_", "")))

    if request.method == "POST" and "leniwa" == list(request.form.keys())[0].split("_")[0]:
        print("leniwa id", int(list(request.form.keys())[0].replace("leniwa_", "")))

    if request.method == "POST" and "leniwaSkos" == list(request.form.keys())[0].split("_")[0]:
        print("leniwaSkos id", int(list(request.form.keys())[0].replace("leniwaSkos_", "")))

    if request.method == "POST" and "owatyWydane" in list(request.form.keys())[0].split("_")[0]:
        print("owatyWydane id", int(list(request.form.keys())[0].replace("owatyWydane_", "")))

    if request.method == "POST" and "owatyWyciete" in list(request.form.keys())[0].split("_")[0]:
        print("owatyWyciete id", int(list(request.form.keys())[0].replace("owatyWyciete_", "")))

    if request.method == "POST" and "owatyKompletacja" in list(request.form.keys())[0].split("_")[0]:
        print("owatyKompletacja id", int(list(request.form.keys())[0].replace("owatyKompletacja_", "")))

    if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
        # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
        return redirect(url_for("wydzial_pianek.raport_jakosciowy", id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("plan_pracy.html", title="PLAN PRACY", plan_pracy={"plan_pracy":json_plan_pracy})