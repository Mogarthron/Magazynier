from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session
from sqlalchemy import text
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Pianki.Analiza_pianek.Podsumowanie_analizy_pianek import Podsumowanie_analizy_pianek

from ..analiza_pianek import analiza_pianek


ard = {x.MODEL: x for x in izp}
pap = Podsumowanie_analizy_pianek(izp)

zam_pianki = dict()

@analiza_pianek.route("/")
def index():
    return render_template("analiza_pianek.html", title="Analiza pianek", pap=pap)

@analiza_pianek.route("/dokumentacja_pianek/<numer>")
def dokumentacja_pianek_numer(numer):
    dokumentacja = [list(x) for x in session.execute(text(f"SELECT MODEL, BRYLA, TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where NUMER = '{numer}'")).fetchall()]

    return [list(x) for x in dokumentacja]


@analiza_pianek.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):

    if request.method == "POST" and "dodajBryly" in request.form.keys():
        bryly_do_zamowienia = {k:v for k,v in request.form.lists()}
        zam_pianki[model] = {}
        for i in range(len(bryly_do_zamowienia["bryla"])):
            zam_pianki[model][f"{bryly_do_zamowienia['bryla'][i]}"] = float(bryly_do_zamowienia['ile'][i])

        print(zam_pianki)

    elif request.method == "POST" and "sprawdzObj" in request.form.keys():
        _lista_korekty_zam = {k:v for k,v in request.form.lists()}
        lista_korekty_zam = dict()
        for i in range(len(_lista_korekty_zam["bryla"])):
            lista_korekty_zam[f"{_lista_korekty_zam['bryla'][i]}"] = float(_lista_korekty_zam['ile'][i])
        
        # print(lista_korekty_zam)
        cls = ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=lista_korekty_zam)[1]

        _model = model + f" PIANPOL:{cls.pianpol_VOL:.0f}, VITA:{cls.vita_VOL:.0f}, CIECH:{cls.ciech_VOL:.0f}"
        
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=_model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=lista_korekty_zam))
    


    return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True))

@analiza_pianek.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    if request.method == "POST" and "przejdz_do_bryly" in request.form.keys():
    
        return redirect(url_for("analiza_pianek.dodaj_pianki_bryla", model=request.form["model"]))
    
    if request.method == "POST" and "wyczysc_bryly" in request.form.keys():
    
        zam_pianki = {}

    return render_template("dodaj_pianki_model.html", title="Dodaj Pianki", lista_modeli = list([x.MODEL for x in izp])) 

