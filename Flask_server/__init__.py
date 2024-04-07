from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
# from Analiza_pianek import Podsumowanie_analizy_pianek
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Modele_db import *
from Modele_db.modele_db import *
from datetime import datetime as dt, timedelta
# import pandas as pd
from sqlalchemy import or_

from Flask_server.kalendarz_dostaw import kal_dos


app = Flask(__name__)
# pap = Podsumowanie_analizy_pianek(izp)
ard = {x.MODEL: x for x in izp}

@app.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):
    
    return render_template("dodaj_pianki_bryla.html", model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True))

@app.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    if request.method == "POST":
        print(request.form["model"])
        return redirect(url_for("dodaj_pianki_bryla", model=request.form["model"]))

    return render_template("dodaj_pianki_model.html", lista_modeli = list([x.MODEL for x in izp])) 



@app.route("/plan_pracy_wydzialu_pianek", methods=["GET", "POST"])
def paln_pracy_wydzialu_pianek():

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

    return render_template("plan_pracy_wydzialu_pianek.html", plan_pracy={"plan_pracy":json_plan_pracy})


@app.route("/")
def index():
    # return "ddd"
    iz = list(map(lambda x: x.Raport(), izp))
    return render_template("index.html", iz = {"Raport": iz})   

@app.route("/kalendarz_dostaw")
def kalendarz_dostaw():

        
    lista_dni = list()
    start_mc = 3
    start_d = 25
    tygodni_do_przodu = 7

    for i in range(tygodni_do_przodu):
        pierwszy_dzien = dt(2024,start_mc,start_d)+timedelta(7*i)
        tydzien = dt.isocalendar(pierwszy_dzien).week
        # lista_dni.append([tydzien] + [(pierwszy_dzien + timedelta(x)).strftime("%d-%b") for x in range(5)])
        lista_dni.append([tydzien] + [(pierwszy_dzien + timedelta(x)) for x in range(5)])

    
    return render_template("kalendarz_dostaw.html", lista_dni=lista_dni, kal_dos=kal_dos)



