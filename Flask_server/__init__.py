from flask import Flask, render_template
from datetime import datetime as dt, timedelta


from Flask_server.kalendarz_dostaw import kal_dos

from Flask_server.Bluprints.wydzial_pianek import wydzial_pianek
from Flask_server.Bluprints.analiza_pianek import analiza_pianek
from Flask_server.Bluprints.magazyny_pianki import magazyny_pianki
from Flask_server.Bluprints.poduszki import poduszki


app = Flask(__name__)

app.secret_key = "Super secret key"

app.register_blueprint(wydzial_pianek, url_prefix="/wydzial_pianek")
app.register_blueprint(analiza_pianek, url_prefix="/analiza_pianek")
app.register_blueprint(magazyny_pianki, url_prefix="/magazyny_pianki")
app.register_blueprint(poduszki, url_prefix="/poduszki")


@app.route("/")
def index():
    
    linki = ["Wydział Pianek"]

    return render_template("index.html", title="Strona Główna")   

@app.route("/reklamacja_email")
def reklamacja_email():

    uwagi_ogolne = ["""Dostawa nie przyjechała do nas w terminie. Po ustaleniach z Panem
        Szymczykiem samochód miał się zjawić u nas 2024-04-15. Transport nie
        znaszej winy został przesunięty o dwa dni.""", 
        """Wszytkie fotele: KELLY, OVAL, GREY przyjechały spakowane po parę sztuk w
        jedną paczkę. W dokumentacji jest jasno napisane jak nleży pakować
        komplety foteli. Prosze o wytłumaczenie podjęcia decyzji o spakowaniu niezgodnie z dokumentacją"""]
    uwagi_ogolne_do_pozycji_dostawie = []
    uwagi_do_pianek = {"DIVA X2,5X 10szt": [["EC0337", "wymiar nie zgodny z dokumentacją"]],
                        "DIVA 3X 5szt": [["EC0336", "wymiar nie zgodny z dokumentacją"]],
                        "DIVA LA 20szt": [["AA2376", "wymiar nie zgodny z dokumentacją"],
                                         ["AA2386", "skos ze złej strony"],
                                         ["AA2387", "skos ze złej strony"],
                                         ["FA0241", "wymiar nie zgodny z dokumentacją, skos ze złej strony"],
                                     ],
                        "DIVA X4X 5szt": [["AA2270", "wymiar nie zgodny z dokumentacją"],
                                          ["DB0168", "wymiar nie zgodny z dokumentacją"],
                                          ["EC0334", "wymiar nie zgodny z dokumentacją"],
                                          ["FA0219", "wymiar nie zgodny z dokumentacją"],]}

  
    return render_template("email_reklamacja.html", nr_reklamacji="CIECH 13_2024", 
                           uwagi_ogolne=uwagi_ogolne, 
                           uwagi_ogolne_do_pozycji_dostawie=uwagi_ogolne_do_pozycji_dostawie,
                           uwagi_do_pianek=uwagi_do_pianek)   



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



