from ..routes import *
from Pianki.Raporty_do_zamowien.Komponowanie_zamowienia import Raport_zamowionych_pianek_i_owat
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
import json
import numpy as np
import os
from flask import flash

@analiza_pianek.route("/dodaj_pianki_model", methods=["GET", "POST"])
def dodaj_pianki_model():

    ard = {x.MODEL: x for x in izp}
    
    if request.method == "POST" and "del" in list(request.form.keys())[0].split("_")[0]:
        
        if len(list(request.form.keys())[0].split("_")[1:]) > 0:
            _model, _bryla = list(request.form.keys())[0].split("_")[1:]           

            global z_pianki
            z_pianki[_model].pop(_bryla)
            if len(z_pianki[_model]) == 0:
                z_pianki.pop(_model)

           
    if request.method == "POST" and "przejdz_do_bryly" in request.form.keys():
        
        return redirect(url_for("analiza_pianek.dodaj_pianki_bryla", model=request.form["model"]))
    
    if request.method == "POST" and "wyczysc_bryly" in request.form.keys() and len(z_pianki) > 0:

        # if len(z_pianki) > 0:            
        #     z_pianki = {}
        z_pianki = {}

    if request.method == "POST" and "generuj_raport_zamowionych_pianek" in request.form.keys() and len(z_pianki) > 0:         
        
        # print(z_pianki)
        if request.form["nr_partii"] and request.form["nr_zamowienia"] and request.form["dostawca"] and request.form["data_dostawy"]:
      
            if os.path.exists("./propozycja_zamowionych_pianek.json"):

                with open("./propozycja_zamowionych_pianek.json",'r') as f:
                    # First we load existing data into a dict.
                    file_data = json.load(f)
                
                with open("./propozycja_zamowionych_pianek.json",'w') as f:
                    # Join new_data with file_data inside emp_details
                    if len(z_pianki)>0:

                        file_data[request.form["nr_partii"]] = {"NR_ZAM":request.form["nr_zamowienia"], "DOSTAWCA":request.form["dostawca"].upper(), "DATA_DOS": request.form["data_dostawy"], "PROP_ZAM": z_pianki}
                    # Sets file's current position at offset.
                    f.seek(0)
                    # convert back to json.
                    json.dump(file_data, f)
                    
            else:         
                with open("propozycja_zamowionych_pianek.json", "w") as f:
                    json.dump({request.form["nr_partii"]: {"NR_ZAM":request.form["nr_zamowienia"], "DOSTAWCA":request.form["dostawca"].upper(), "DATA_DOS": request.form["data_dostawy"], "PROP_ZAM": z_pianki}}
                              ,f)

            return redirect(url_for('analiza_pianek.raport_zamowionych_pianek_i_owat', nr_partii=request.form["nr_partii"].replace("/", "_")))
        
        else: 
            flash("Brak uzupełniego pola")
            print("Brak uzupełniego pola")
    
    if request.method == "POST" and "generuj_raport_zamowionych_pianek" in request.form.keys() and len(z_pianki) == 0:
        flash("DODAJ BRYŁY DO ZESTAWIENIA")    
        print("DODAJ BRYŁY DO ZESTAWIENIA")    

        

    tabela_obietosci = []
    podsumowanie_tabeli_obietosci = ["SUMA","","","",""]
    rolki_owat = []

    if len(z_pianki) > 0:

        print("z_pianki wieksze od 0",z_pianki)

        for k in z_pianki:
            zcls, cls = ard[k].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=z_pianki[k])
            tabela_obietosci.append([k, np.round(cls.pianpol_VOL, 0), np.round(cls.ciech_VOL, 0), np.round(cls.vita_VOL, 0), np.round(cls.olta_VOL, 0)])
            rolki_owat.append(zcls)

        podsumowanie_tabeli_obietosci = ["SUMA", f"{sum([x[1] for x in tabela_obietosci]):.0f}",  f"{sum([x[2] for x in tabela_obietosci]):.0f}",  f"{sum([x[3] for x in tabela_obietosci]):.0f}", f"{sum([x[4] for x in tabela_obietosci]):.0f}"]
        rolki_owat = Raport_zamowionych_pianek_i_owat(rolki_owat)[1]

        return render_template("dodaj_pianki_model.html", title="Dodaj Pianki", lista_modeli = list([x.MODEL for x in izp]), z_pianki=z_pianki, tabela_obietosci=tabela_obietosci, podsumowanie_tabeli_obietosci=podsumowanie_tabeli_obietosci, rolki_owat=rolki_owat) 
    
    else:      
        print("z_pianki == 0",z_pianki)
        return render_template("dodaj_pianki_model.html", title="Dodaj Pianki", lista_modeli = list([x.MODEL for x in izp]), z_pianki=z_pianki, tabela_obietosci=tabela_obietosci, podsumowanie_tabeli_obietosci=podsumowanie_tabeli_obietosci, rolki_owat=rolki_owat) 

