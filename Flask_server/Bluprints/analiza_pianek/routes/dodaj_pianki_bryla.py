from ..routes import *

# ard = {x.MODEL: x for x in izp}
# pap = Podsumowanie_analizy_pianek(izp)

@analiza_pianek.route("/dodaj_pianki_bryla/<model>", methods=["GET", "POST"])
def dodaj_pianki_bryla(model):
    ile_bryl_z_analizy = ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True)
    if request.method == "POST" and "dodajBryly" in request.form.keys():
        bryly_do_zamowienia = {k:v for k,v in request.form.lists()}
        z_pianki[model] = {}
        for i in range(len(bryly_do_zamowienia["bryla"])):
            if float(bryly_do_zamowienia['ile'][i]) > 0:
                z_pianki[model][f"{bryly_do_zamowienia['bryla'][i]}"] = float(bryly_do_zamowienia['ile'][i])

        print("dodaj_pianki_bryla", z_pianki)
        return redirect(url_for('analiza_pianek.dodaj_pianki_model'))

    elif request.method == "POST" and "sprawdzObj" in request.form.keys():
        _lista_korekty_zam = {k:v for k,v in request.form.lists()}
        lista_korekty_zam = dict()
        for i in range(len(_lista_korekty_zam["bryla"])):
            lista_korekty_zam[f"{_lista_korekty_zam['bryla'][i]}"] = float(_lista_korekty_zam['ile'][i])
        
        # print(lista_korekty_zam)
        cls = ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, korekta_zam=lista_korekty_zam)[1]

        _model = model + f" PIANPOL:{cls.pianpol_VOL:.0f}, VITA:{cls.vita_VOL:.0f}, CIECH:{cls.ciech_VOL:.0f}"
        
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=_model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=lista_korekty_zam), ile_bryl_z_analizy=ile_bryl_z_analizy)
    

    if model in z_pianki.keys():
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=z_pianki[model]), ile_bryl_z_analizy=ile_bryl_z_analizy)
    else:
        return render_template("dodaj_pianki_bryla.html", title="Dodaj Bryły - " + model, model=model, bryla=ard[model].Bryly_do_zamowienia(wszystkie_bryly=True, lista_korekty_zam=True), ile_bryl_z_analizy=ile_bryl_z_analizy)


