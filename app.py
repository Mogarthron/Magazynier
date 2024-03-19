from flask import Flask, render_template, request, url_for, flash, redirect
from Analiza_pianek import Podsumowanie_analizy_pianek
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol
from datetime import datetime as dt, timedelta
arp = Podsumowanie_analizy_pianek(instrukcja_zamawiania_pianpol)

app = Flask(__name__)

@app.route("/")
def index():

    return render_template("index.html", tables=[arp.Tabela_podsumowania_analizy.to_html(index=False, classes='table table-striped table-hover', header="true")])   

@app.route("/kalendarz_dostaw")
def kalendarz_dostaw():

    kal_dos = {dt(2024,3,15): {"DOSTAWCA": "PIANPOL",
                          "NR PARTII": "08/01",
                          "NR DOS": "24/0216",
                          "MODELE": "AVA",
                          "OBJ": ["width: 55%;", 55]},
                dt(2024,3,22): {"DOSTAWCA": "VITA",
                          "NR PARTII": "09/01",
                          "NR DOS": "24/0299",
                          "MODELE": "STO, HOR, BLOK T-35",
                          "OBJ": ["width: 99%;", 99]},
                dt(2024,3,20): {"DOSTAWCA": "PIANPOL",
                          "NR PARTII": "08/01",
                          "NR DOS": "24/0216",
                          "MODELE": "MAX, OXY",
                          "OBJ": ["width: 25%;", 25]},
                                              }
    
    lista_dni = list()
    start_mc = 3
    start_d = 11

    for i in range(7):
        pierwszy_dzien = dt(2024,start_mc,start_d)+timedelta(7*i)
        tydzien = dt.isocalendar(pierwszy_dzien).week
        # lista_dni.append([tydzien] + [(pierwszy_dzien + timedelta(x)).strftime("%d-%b") for x in range(5)])
        lista_dni.append([tydzien] + [(pierwszy_dzien + timedelta(x)) for x in range(5)])

    
    return render_template("kalendarz_dostaw.html", lista_dni=lista_dni, kal_dos=kal_dos)



if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

