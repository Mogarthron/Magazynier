from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
# from Analiza_pianek import Podsumowanie_analizy_pianek
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Modele_db import *
from Modele_db.modele_db import *
from datetime import datetime as dt, timedelta
# import pandas as pd
from sqlalchemy import or_


app = Flask(__name__)
# pap = Podsumowanie_analizy_pianek(izp)


@app.route("/plan_pracy_wydzialu_pianek", methods=["GET", "POST"])
def paln_pracy_wydzialu_pianek():

    plan_pracy = session.query(ZAM_PIANKI).filter(
                    or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
    
    json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))
    
    return render_template("plan_pracy_wydzialu_pianek.html", plan_pracy={"plan_pracy":json_plan_pracy})


@app.route("/")
def index():
    # return "ddd"
    iz = list(map(lambda x: x.Raport(), izp))
    return render_template("index.html", iz = {"Raport": iz})   

@app.route("/kalendarz_dostaw")
def kalendarz_dostaw():

    kal_dos = {
                dt(2024,3,27): [{"DOSTAWCA": "PIANPOL",
                          "NR PARTII": "08/01",
                          "NR DOS": "24/0216",
                          "MODELE": "MAX, OXY",
                          "OBJ": ["width: 40%;", 40]},],
                dt(2024,4,4): [{"DOSTAWCA": "OWATY",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "REV, SAM",
                          "OBJ": []}],
                dt(2024,4,5): [{"DOSTAWCA": "PIANPOL",
                          "NR PARTII": "10/01",
                          "NR DOS": "24/0299",
                          "MODELE": "AVA, ELI, REV",
                          "OBJ": ["width: 74%;", 74]},

                          {"DOSTAWCA": "OWATY",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "REV, SAM",
                          "OBJ": []}],
            
                dt(2024,4,15): [{"DOSTAWCA": "CIECH",
                          "NR PARTII": "11/01",
                          "NR DOS": "24/0327",
                          "MODELE": "SAM, DIV, GRE, OVA, CAL, KEL",
                          "OBJ": ["width: 83%;", 83]},],
                dt(2024,4,19): [{"DOSTAWCA": "PIANPOL",
                          "NR PARTII": "12/01",
                          "NR DOS": "24/0347",
                          "MODELE": "REV, AVA",
                          "OBJ": ["width: 78%;", 78]},],   
                dt(2024,4,29): [{"DOSTAWCA": "WOLNE",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "",
                          "OBJ": []},],    
                dt(2024,4,30): [{"DOSTAWCA": "WOLNE",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "",
                          "OBJ": []},],    
                dt(2024,5,1): [{"DOSTAWCA": "WOLNE",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "",
                          "OBJ": []},],    
                dt(2024,5,2): [{"DOSTAWCA": "WOLNE",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "",
                          "OBJ": []},],    
                dt(2024,5,3): [{"DOSTAWCA": "WOLNE",
                          "NR PARTII": "",
                          "NR DOS": "",
                          "MODELE": "",
                          "OBJ": []},],                                                           
                                              }
    
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



# @app.route("/analiza_pianek")
# def analiza_pianek():    

#     return render_template("analiza_pianek.html", pap=pap)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

