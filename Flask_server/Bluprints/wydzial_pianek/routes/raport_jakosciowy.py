from ..routes import *
from Flask_server.Bluprints.wydzial_pianek.funkcje_pomocnicze import raport_jakosciowy_dane



@wydzial_pianek.route("/raport_jakosciowy/", defaults={"id": None, "nr_samochodu": None})
@wydzial_pianek.route("/raport_jakosciowy/<nr_samochodu>/<id>", methods=["GET", "POST"])
def raport_jakosciowy(nr_samochodu, id):
    
    if id:
               
        model, bryla_gen, opis, ile_zam, tabelka_kj = raport_jakosciowy_dane(id)

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

        # print(opis)
        # print(pd.DataFrame(tabelka_kj))
        # print(tabelka_kj)
        return render_template("raport_jakosciowy.html", opis=opis, ile_zam=ile_zam, tabelka_kj=tabelka_kj, nr_samochodu=nr_samochodu)
    
    else:
        
        kj = RAPORT_KJ_DO_DOSTAWY_PIANEK
               
        res = session.query(kj)   

        json_kj = list(map(lambda x: x.kj_to_json(), res))
        return json_kj
    