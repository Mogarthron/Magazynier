# from flask import render_template, request, redirect, url_for
# from Modele_db.modele_db import session, ZAM_PIANKI, RAPORT_KJ_DO_DOSTAWY_PIANEK#, AKTYWNE_DOSTAWY 
# from Modele_db import engine
# from sqlalchemy import or_, text

# from Pianki.Dostawy_pianek import wykers_zapelnienia_samochodow#, obietosci_samochodow
# import plotly.express as px
# import plotly

# from ..wydzial_pianek import wydzial_pianek
# from Flask_server.Blupints.wydzial_pianek.funkcje_pomocnicze import *

# import pandas as pd

# @wydzial_pianek.route("/")
# def index():   


#     return render_template("wydzial_pianek.html", title="Wydział pianek")

# @wydzial_pianek.route("/naklejki")
# def naklejki():

#     with engine.begin() as conn:
#         zp = conn.execute(text(f"""SELECT MODEL, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE,
#                         NR_PARTII from ZAM_PIANKI WHERE ZAM1 in('24/0486') --AND OPIS NOT LIKE '%AVANT%'"""))
    
#     zam_pianki = zp.fetchall()

#     wiersze = list()

#     for row in zam_pianki:
        
#         for i in range(row[3]):
            
#             wiersze.append([row[4], row[1], f"{i+1}/{row[3]}", row[0], row[2].replace(row[0], "").strip()])
          

#     return render_template("naklejki_na_paczki_pianek_zebra.html", wiersze=wiersze)

# @wydzial_pianek.route("/dostawy_pianek")
# def dostawy_pianek():

#     from ..wydzial_pianek.tabela_dostaw_pianek import tabelka_dostawy_pianek, df
       
#     fig = wykers_zapelnienia_samochodow(df)
    
#     return render_template("dostawy_pianek.html", title="Dostawy pianek", 
#                                                   tabelka_dostawy_pianek=tabelka_dostawy_pianek,  
#                                                   graphJSON=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


# @wydzial_pianek.route("/przyjecie_dostawy/<nr_samochodu>", methods=["GET", "POST"])
# def przyjecie_dostawy(nr_samochodu):
    
#     pianki_w_drodze = session.query(ZAM_PIANKI).filter(ZAM_PIANKI.nr_samochodu.like(f"%{nr_samochodu}%")).all()
    
#     json_pianki_w_drodze = list(map(lambda x: x.pianki_w_drodze_to_json(), pianki_w_drodze))
    
#     raport_realizacji_dostawy = [
#         ["ADAM RZEPKO", 57, 190, 0, 0, 0],
#         ["PIOTR ŁUPIŃSKI", 57, 0, 0, 305, 225],
#         ["PAWEŁ MIŚKO", 57, 0, 0, 165, 225],
#     ]

#     if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
#         # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
#         return redirect(url_for("wydzial_pianek.raport_jakosciowy", nr_samochodu=nr_samochodu ,id=int(list(request.form.keys())[0].replace("kj_", ""))))

#     return render_template("przyjecie_dostawy.html", title=f"Przyjecie dostawy {nr_samochodu}", 
#                                                         nr_samochodu=nr_samochodu, 
#                                                         raport_realizacji_dostawy=raport_realizacji_dostawy,
#                                                         pianki_w_drodze={"pianki_w_drodze":json_pianki_w_drodze})



# @wydzial_pianek.route("/raport_jakosciowy/", defaults={"id": None, "nr_samochodu": None})
# @wydzial_pianek.route("/raport_jakosciowy/<nr_samochodu>/<id>", methods=["GET", "POST"])
# def raport_jakosciowy(nr_samochodu, id):
    
#     if id:
               
#         model, bryla_gen, opis, ile_zam, tabelka_kj = raport_jakosciowy_dane(id)

#         #['uwagiDlugosc', 'bladAkceptowanyDlugosc', 'uwagiSzerokosc', 'bladAkceptowanySzerokosc', 'uwagiWysokosc', 'bladAkceptowanyWysokosc', 'uwagiInne', 'pozycjaDoReklamacji', 'numerPaczki_1']
#         if request.method == "POST":
            
#             numery_z_formy = list(request.form.keys())[-1].split("_")
#             nr_paczki = numery_z_formy[1]
#             nr_pianki = numery_z_formy[3]
#             blad_dopuszczalny_wysokosc = 1 if type(request.form.get("bladAkceptowanyWysokosc")) == str else 0 
#             blad_dopuszczalny_szerokosc = 1 if type(request.form.get("bladAkceptowanySzerokosc")) == str else 0 
#             blad_dopuszczalny_dlugosc = 1 if type(request.form.get("bladAkceptowanyDlugosc")) == str else 0 
#             blad_dopuszczalny = 1 if type(request.form.get("pozycjaDoReklamacji")) == str else 0 
            
#             session.add(RAPORT_KJ_DO_DOSTAWY_PIANEK(id, nr_paczki, model, bryla_gen, nr_pianki, 
#                                                     blad_dopuszczalny_wysokosc, request.form["uwagiWysokosc"], 
#                                                     blad_dopuszczalny_szerokosc, request.form["uwagiSzerokosc"],
#                                                     blad_dopuszczalny_dlugosc, request.form["uwagiDlugosc"], 
#                                                     blad_dopuszczalny, request.form["uwagiInne"]))

#             session.commit()

#         # print(opis)
#         # print(pd.DataFrame(tabelka_kj))
#         return render_template("raport_jakosciowy.html", opis=opis, ile_zam=ile_zam, tabelka_kj=tabelka_kj, nr_samochodu=nr_samochodu)
    
#     else:
        
#         kj = RAPORT_KJ_DO_DOSTAWY_PIANEK
               
#         res = session.query(kj)   

#         json_kj = list(map(lambda x: x.kj_to_json(), res))
#         return json_kj
    

# @wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
# def plan_pracy():

#     plan_pracy = session.query(ZAM_PIANKI).filter(
#                     or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
    
#     json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))


#     if request.method == "POST" and "zakonczono" in list(request.form.keys())[0]:
#         print("zakonczono id", int(list(request.form.keys())[0].replace("zakonczono_", "")))
        
#     if request.method == "POST" and "edytuj" in list(request.form.keys())[0]:
#         print("edytuj id", int(list(request.form.keys())[0].replace("edytuj_", "")))

#     if request.method == "POST" and "leniwa" == list(request.form.keys())[0].split("_")[0]:
#         print("leniwa id", int(list(request.form.keys())[0].replace("leniwa_", "")))

#     if request.method == "POST" and "leniwaSkos" == list(request.form.keys())[0].split("_")[0]:
#         print("leniwaSkos id", int(list(request.form.keys())[0].replace("leniwaSkos_", "")))

#     if request.method == "POST" and "owatyWydane" in list(request.form.keys())[0].split("_")[0]:
#         print("owatyWydane id", int(list(request.form.keys())[0].replace("owatyWydane_", "")))

#     if request.method == "POST" and "owatyWyciete" in list(request.form.keys())[0].split("_")[0]:
#         print("owatyWyciete id", int(list(request.form.keys())[0].replace("owatyWyciete_", "")))

#     if request.method == "POST" and "owatyKompletacja" in list(request.form.keys())[0].split("_")[0]:
#         print("owatyKompletacja id", int(list(request.form.keys())[0].replace("owatyKompletacja_", "")))

#     if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
#         # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
#         return redirect(url_for("wydzial_pianek.raport_jakosciowy", id=int(list(request.form.keys())[0].replace("kj_", ""))))

#     return render_template("plan_pracy.html", title="PLAN PRACY", plan_pracy={"plan_pracy":json_plan_pracy})