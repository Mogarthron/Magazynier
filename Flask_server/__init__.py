from flask import Flask, render_template
from datetime import datetime as dt, timedelta


from Flask_server.kalendarz_dostaw import kal_dos

from Flask_server.Bluprints.wydzial_pianek import wydzial_pianek
from Flask_server.Bluprints.analiza_pianek import analiza_pianek


app = Flask(__name__)
app.register_blueprint(wydzial_pianek, url_prefix="/wydzial_pianek")
app.register_blueprint(analiza_pianek, url_prefix="/analiza_pianek")


@app.route("/")
def index():
  
    return render_template("index.html", title="Strona Główna")   

@app.route("/reklamacja_email")
def reklamacja_email():
  
    return render_template("email_reklamacja.html")   



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



