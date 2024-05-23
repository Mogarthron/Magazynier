# from flask import render_template, request, redirect, url_for
# from Modele_db.modele_db import session
# from sqlalchemy import text
# from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
# from Pianki.Analiza_pianek.Podsumowanie_analizy_pianek import Podsumowanie_analizy_pianek

# from analiza_pianek import analiza_pianek


# ard = {x.MODEL: x for x in izp}
# pap = Podsumowanie_analizy_pianek(izp)


# z_pianki = dict()
import json
import os

from ..routes import *

import numpy as np

@analiza_pianek.route("/")
def index():
    return render_template("analiza_pianek.html", title="Analiza pianek", pap=pap)

@analiza_pianek.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):

    if request.method == "POST" and "dodajBryly" in request.form.keys():
        bryly_do_zamowienia = {k:v for k,v in request.form.lists()}
        z_pianki[model] = {}
        for i in range(len(bryly_do_zamowienia["bryla"])):
            if float(bryly_do_zamowienia['ile'][i]) > 0:
                z_pianki[model][f"{bryly_do_zamowienia['bryla'][i]}"] = float(bryly_do_zamowienia['ile'][i])

        # print(z_pianki)
        return redirect(url_for('analiza_pianek.dodaj_pianki_model'))

    elif request.method == "POST" and "sprawdzObj" in request.form.keys():
        _lista_korekty_zam = {k:v for k,v in request.form.lists()}
        lista_korekty_zam = dict()
        for i in range(len(_lista_korekty_zam["bryla"])):
            lista_korekty_zam[f"{_lista_korekty_zam['bryla'][i]}"] = float(_lista_korekty_zam['ile'][i])
        
        # print(lista_korekty_zam)
        cls = ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=lista_korekty_zam)[1]

        _model = model + f" PIANPOL:{cls.pianpol_VOL:.0f}, VITA:{cls.vita_VOL:.0f}, CIECH:{cls.ciech_VOL:.0f}"
        
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=_model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=lista_korekty_zam))
    

    if model in z_pianki.keys():
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=z_pianki[model]))
    else:
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True))



@analiza_pianek.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    if request.method == "POST" and "del" in list(request.form.keys())[0].split("_")[0]:
        
        if len(list(request.form.keys())[0].split("_")[1:]) > 0:
            _model, _bryla = list(request.form.keys())[0].split("_")[1:]           

            global z_pianki
            z_pianki[_model].pop(_bryla)

           
    if request.method == "POST" and "przejdz_do_bryly" in request.form.keys():
        
        return redirect(url_for("analiza_pianek.dodaj_pianki_bryla", model=request.form["model"]))
    
    if request.method == "POST" and "wyczysc_bryly" in request.form.keys() and len(z_pianki) > 0:

        # if len(z_pianki) > 0:            
        #     z_pianki = {}
        z_pianki = {}

    if request.method == "POST" and "generuj_raport_zamowionych_pianek" in request.form.keys() and len(z_pianki) > 0: 
        
        print(z_pianki)  
        print(os.listdir(""))


    tabela_obietosci = []
    podsumowanie_tabeli_obietosci = ["SUMA","","",""]
    if len(z_pianki) > 0:
        for k in z_pianki:
            cls = ard[k].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=z_pianki[k])[1]
            tabela_obietosci.append([k, np.round(cls.pianpol_VOL, 0), np.round(cls.ciech_VOL, 0), np.round(cls.vita_VOL, 0)])

        podsumowanie_tabeli_obietosci = ["SUMA", f"{sum([x[1] for x in tabela_obietosci]):.0f}",  f"{sum([x[2] for x in tabela_obietosci]):.0f}",  f"{sum([x[3] for x in tabela_obietosci]):.0f}"]

    return render_template("dodaj_pianki_model.html", title="Dodaj Pianki", lista_modeli = list([x.MODEL for x in izp]), z_pianki=z_pianki, tabela_obietosci=tabela_obietosci, podsumowanie_tabeli_obietosci=podsumowanie_tabeli_obietosci) 

