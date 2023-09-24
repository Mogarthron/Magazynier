from flask import Flask, render_template
import plotly
import plotly.express as px
import json
import pandas as pd
from datetime import datetime as dt, timedelta
import sqlite3

cnn = sqlite3.connect("mydb.db")
cur = cnn.execute("select nazwa_magazynu from Magazyn")
magazyny = [x[0] for x in cur.fetchall()]
dos_pianki = []

# magazyny = {"mag1":{"nazwa_mag": "Magazyn 1","regaly": {"Regał 1":{"Półka 1": "6pak 3860"}}}, "mag2":{"nazwa_mag": "Magazyn 2"}, "mag3":{"nazwa_mag": "Magazyn 3"}, "mag4":{"nazwa_mag": "Magazyn 4"}}


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", magazyny = magazyny)    

# @app.route("/magazyn/<mag>")
# def magazyn(mag=None):        
#     return render_template("magazyn.html", mag=magazyny[mag])

@app.route("/mag1")
def mag1():
    return "Magazyn 1"

@app.route("/dostawy_pianek")
def dostawy_pianek():

    _dostawy = [
        dict(NR_Dostawy="23/0956", Dostawca="PIANPOL", Data_Dostawy=dt(2023,9,26), Opis="AVA, OVAL"),
        dict(NR_Dostawy="23/1008", Dostawca="CIECH", Data_Dostawy=dt(2023,10,2), Opis="DIV, HUD, EXT, HOR Len, ONY Len"),
        dict(NR_Dostawy="23/1010", Dostawca="VITA", Data_Dostawy=dt(2023,10,5), Opis="ONY, HOR, EXT"),
        dict(NR_Dostawy="23/1041", Dostawca="VITA", Data_Dostawy=dt(2023,10,9), Opis="STO, KELLY, BLOK T25 i T35"),
        dict(NR_Dostawy="23/1040", Dostawca="CIECH", Data_Dostawy=dt(2023,10,9), Opis="ELI, CAL, HUD, REV, WIL, GRE, LEN"),
        dict(NR_Dostawy="23/1096", Dostawca="PIANPOL", Data_Dostawy=dt(2023,10,12), Opis="AVA, OVAL"),
        dict(NR_Dostawy="23/1098", Dostawca="VITA", Data_Dostawy=dt(2023,10,17), Opis="REV, AMA,ELI, WIL"),
        dict(NR_Dostawy="23/1097", Dostawca="CIECH", Data_Dostawy=dt(2023,10,18), Opis="AMA, ELI, WIL")
    ]


    dos = pd.DataFrame(_dostawy)
    dos["data_dos"] = dos.Data_Dostawy + timedelta(1)

    fig = px.timeline(dos, x_start="Data_Dostawy", x_end="data_dos", y="Dostawca", title="Dostawy pianek", text="NR_Dostawy", hover_data=["Opis",], color="Dostawca")
    fig.add_vline(x=dt.now(), line_width=.5, line_color="blue")
    fig.update_yaxes(autorange="reversed")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("dostawy_pianek.html", graphJSON=graphJSON, dostawy=dos[["NR_Dostawy", "Dostawca", "Data_Dostawy", "Opis"]])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

