from ..routes import *
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Modele_db import session
from Modele_db.modele_db import ZAM_PIANKI



import json
from datetime import datetime as dt



@analiza_pianek.route("/zapis_do_bazy/<nr_partii>", methods=["GET", "POST"])
def zapis_do_bazy(nr_partii):   
    
    nr_partii = nr_partii.replace("_", "/")
    dizp = {x.MODEL:x for x in izp}
    
    with open("propozycja_zamowionych_pianek.json", "r") as f:
        pozycje_do_zapisu = json.load(f)[nr_partii]


    
    dostawca = pozycje_do_zapisu["DOSTAWCA"]
    nr_zamowienia = pozycje_do_zapisu["NR_ZAM"]

    informacje_model = {}
    for pdz in pozycje_do_zapisu["PROP_ZAM"]:
        kompl = []
        for i in session.query(ZAM_PIANKI.nr_kompletacji).filter(ZAM_PIANKI.model == pdz).distinct().all():
            kompl.append([i[0].split("_")[1], i[0].split("_")[0]])
        kompl.sort(key=lambda x: x[0])
        kompl = kompl[-1][::-1]
        kompl[0] = str(int(kompl[0]) + 1)
            
        informacje_model[pdz] = {"ZNACZNIK_DOSTAWCY": dizp[pdz].klasa.__name__.split("_")[1],
                                 "NR_KOMPLETACJI": "_".join(kompl) }


    tydzien = (dt.now().isocalendar().year - 2000)*100 + dt.now().isocalendar().week
    
    if request.method == "POST":
       
        lista_danych_do_zamowienia = {
                                    "nr_partii": None,                                   
                                    "znacznik_dostawcy": None,
                                    "nr_kompletacji": None,
                                    "zam1": None,
                                    "zam2": None
                                      }
        for i in list(request.form.lists())[1:]:
            model, opis = i[0].split(" ")
            lista_danych_do_zamowienia[opis] = i[1][0]

    
        lista_danych_do_zamowienia["tydzien"] = int(list(request.form.lists())[0][1][0])
      
        modele, klasa = dizp[model].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=pozycje_do_zapisu["PROP_ZAM"][model])
        # print(modele, klasa)

        from Pianki.Raporty_do_zamowien import Dodaj_pozycje_do_ZAM_PIANKI
        print(Dodaj_pozycje_do_ZAM_PIANKI(tydzien=int(list(request.form.lists())[0][1][0]),
                                    zancznik_dostawcy=lista_danych_do_zamowienia["znacznik_dostawcy"],
                                    nr_kompletacji=lista_danych_do_zamowienia["nr_kompletacji"],
                                    modele=modele,
                                    klasa=klasa,
                                    zam1=lista_danych_do_zamowienia["zam1"],
                                    zam2=lista_danych_do_zamowienia["zam2"],
                                    nr_partii=lista_danych_do_zamowienia["nr_partii"]
                                    ))

            





    return render_template("zapis_do_bazy.html", nr_partii=nr_partii, dostawca=dostawca, tydzien=str(tydzien), nr_zamowienia=nr_zamowienia, pozycje_do_zapisu=pozycje_do_zapisu, informacje_model=informacje_model)