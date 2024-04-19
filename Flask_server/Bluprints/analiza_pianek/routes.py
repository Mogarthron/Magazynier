from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session
from sqlalchemy import text
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp

from ..analiza_pianek import analiza_pianek


ard = {x.MODEL: x for x in izp}

@analiza_pianek.route("/")
def index():
    return render_template("index.html", title="Analiza pianek")

@analiza_pianek.route("/dokumentacja_pianek/<numer>")
def dokumentacja_pianek_numer(numer):
    dokumentacja = [list(x) for x in session.execute(text(f"SELECT MODEL, BRYLA, TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where NUMER = '{numer}'")).fetchall()]

    return [list(x) for x in dokumentacja]


@analiza_pianek.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):

    if request.method == "POST":
        print({k:v for k,v in request.form.lists()})
        print(request.form.getlist("ile"))
        # print(request.form["dodajBryly"])


    return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True))

@analiza_pianek.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    if request.method == "POST":
    
        return redirect(url_for("analiza_pianek.dodaj_pianki_bryla", model=request.form["model"]))

    return render_template("dodaj_pianki_model.html", title="Dodaj Pianki", lista_modeli = list([x.MODEL for x in izp])) 

