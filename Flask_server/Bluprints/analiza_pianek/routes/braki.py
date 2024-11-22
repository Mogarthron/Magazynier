from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session
from sqlalchemy import text
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Pianki.Analiza_pianek.Podsumowanie_analizy_pianek import Podsumowanie_analizy_pianek
from Pianki.Analiza_pianek.funkcje_analizy_pianek import *

from Flask_server.Bluprints.analiza_pianek import analiza_pianek
from ..routes import *

# ard = {x.MODEL: x for x in izp}
# pap = Podsumowanie_analizy_pianek(izp)
# z_pianki = dict()

@analiza_pianek.route("/braki")
def braki():
    
    br = Braki(WOLNE="SALDO")[0] #USUNAC PROBLEM Z DUBLUJACYMI SIE ZAMOWIANIAMI(JEDNO DOSTARCZONE DRUGIE W DRODZE TWORZĄ SIĘ DWIE POZYCJE)
    
    return render_template("braki.html", 
                           title="Braki",                           
                           braki=br.sort_values(by=["GRUPA", "OPIS"]).drop("SALDO", axis=1).drop_duplicates("OPIS"), 
                           )