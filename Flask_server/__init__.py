from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Modele_db import *
from Modele_db.modele_db import *
from datetime import datetime as dt, timedelta
from sqlalchemy import or_, select

from Flask_server.kalendarz_dostaw import kal_dos


app = Flask(__name__)

ard = {x.MODEL: x for x in izp}


@app.route("/dokumentacja_pianek/<numer>")
def dokumentacja_pianek_numer(numer):
    dokumentacja = [list(x) for x in session.execute(text(f"SELECT MODEL, BRYLA, TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where NUMER = '{numer}'")).fetchall()]

    return [list(x) for x in dokumentacja]


@app.route("/raport_jakosciowy_pianek/", defaults={"id": None})
@app.route("/raport_jakosciowy_pianek/<id>", methods=["GET", "POST"])
def raport_jakosciowy_pianek(id):
    
    if id:
        
        bryla_jakosc = select(ZAM_PIANKI.kod ,ZAM_PIANKI.model, ZAM_PIANKI.nr_kompletacji, ZAM_PIANKI.opis, ZAM_PIANKI.ile_zam, ZAM_PIANKI.zam1, ZAM_PIANKI.zam2).where(
            ZAM_PIANKI.lp == id)

        kod, model, nr_kompletacji, opis, ile_zam, zam1, zam2 = session.execute(bryla_jakosc).first()
        bryla_gen = session.execute(select(
                                    KOMPLETY_PIANEK.kod, KOMPLETY_PIANEK.bryla_gen).where(KOMPLETY_PIANEK.kod == kod)).first()[1]

        tabelka_kj = [list(x) for x in session.execute(text(f"SELECT TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where MODEL = '{model}' and BRYLA = '{bryla_gen}'")).fetchall()]

        # uwagi_do_wymiaru = session.execute(select(

        #['uwagiDlugosc', 'bladAkceptowanyDlugosc', 'uwagiSzerokosc', 'bladAkceptowanySzerokosc', 'uwagiWysokosc', 'bladAkceptowanyWysokosc', 'uwagiInne', 'pozycjaDoReklamacji', 'numerPaczki_1']
        if request.method == "POST":
            
            numery_z_formy = list(request.form.keys())[-1].split("_")
            nr_paczki = numery_z_formy[1]
            nr_pianki = numery_z_formy[3]
            blad_dopuszczalny_wysokosc = 1 if type(request.form.get("bladAkceptowanyWysokosc")) == str else 0 
            blad_dopuszczalny_szerokosc = 1 if type(request.form.get("bladAkceptowanySzerokosc")) == str else 0 
            blad_dopuszczalny_dlugosc = 1 if type(request.form.get("bladAkceptowanyDlugosc")) == str else 0 
            blad_dopuszczalny = 1 if type(request.form.get("pozycjaDoReklamacji")) == str else 0 
            
            session.add(RAPORT_KJ_DO_DOSTAWY_PIANEK(id, nr_paczki, model, bryla_gen, nr_pianki, 
                                                    blad_dopuszczalny_wysokosc, request.form["uwagiWysokosc"], 
                                                    blad_dopuszczalny_szerokosc, request.form["uwagiSzerokosc"],
                                                    blad_dopuszczalny_dlugosc, request.form["uwagiDlugosc"], 
                                                    blad_dopuszczalny, request.form["uwagiInne"]))

            session.commit()


        return render_template("raport_jakosciowy_pianek.html", opis=opis, ile_zam=ile_zam, tabelka_kj=tabelka_kj)
    
    else:
        
        kj = RAPORT_KJ_DO_DOSTAWY_PIANEK

        res = session.execute(select(kj.bryla_gen, kj.nr_pianki, kj.blad_dopuszczalny_wysokosc, kj.blad_dopuszczalny_dlugosc, kj.blad_dopuszczalny_szerokosc, kj.uwaga_wysokosc, kj.uwaga_dlugosc, kj.uwaga_szerokosc))   

        return [list(x) for x in res]


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

    if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
        # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
        return redirect(url_for("raport_jakosciowy_pianek", id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("plan_pracy_wydzialu_pianek.html", plan_pracy={"plan_pracy":json_plan_pracy})


@app.route("/")
def index():
    return "ddd"
    # iz = list(map(lambda x: x.Raport(), izp))
    # return render_template("index.html", iz = {"Raport": iz})   

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



