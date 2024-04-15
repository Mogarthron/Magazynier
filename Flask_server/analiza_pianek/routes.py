from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session
from sqlalchemy import text
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp

from ..analiza_pianek import analiza_pianek


ard = {x.MODEL: x for x in izp}

@analiza_pianek.route("/dokumentacja_pianek/<numer>")
def dokumentacja_pianek_numer(numer):
    dokumentacja = [list(x) for x in session.execute(text(f"SELECT MODEL, BRYLA, TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where NUMER = '{numer}'")).fetchall()]

    return [list(x) for x in dokumentacja]


@analiza_pianek.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):
    
    return render_template("dodaj_pianki_bryla.html", model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True))

@analiza_pianek.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    if request.method == "POST":
        print(request.form["model"])
        return redirect(url_for("dodaj_pianki_bryla", model=request.form["model"]))

    return render_template("dodaj_pianki_model.html", lista_modeli = list([x.MODEL for x in izp])) 

