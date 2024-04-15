from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session, ZAM_PIANKI, KOMPLETY_PIANEK, RAPORT_KJ_DO_DOSTAWY_PIANEK 
from sqlalchemy import or_, select, text

from ..wydzial_pianek import wydzial_pianek



@wydzial_pianek.route("/raport_jakosciowy/", defaults={"id": None})
@wydzial_pianek.route("/raport_jakosciowy/<id>", methods=["GET", "POST"])
def raport_jakosciowy(id):
    
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


        return render_template("raport_jakosciowy.html", opis=opis, ile_zam=ile_zam, tabelka_kj=tabelka_kj)
    
    else:
        
        kj = RAPORT_KJ_DO_DOSTAWY_PIANEK
               
        res = session.query(kj)   

        json_kj = list(map(lambda x: x.kj_to_json(), res))
        return json_kj
    

@wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
def paln_pracy():

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
        return redirect(url_for("wydzial_pianek.raport_jakosciowy", id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("plan_pracy.html", plan_pracy={"plan_pracy":json_plan_pracy})