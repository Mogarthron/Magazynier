from ..routes import *
from Pianki.Raporty_do_zamowien.raporty_do_zamowien import dane_zam_pianki_czasy, drukuj_raporty, drukuj_raporty_xlsx, naklejki_na_paczki_pianek
from flask import send_file

@analiza_pianek.route("/raporty_do_zamowien", methods=["GET", "POST"])
def raporty_do_zamowien():
    
    if request.method == "POST":
        nr_partii = request.form["nr_partii"]
        zlecenie = request.form["typ_zlecenia"]
        zam = request.form["zam"]
        dostawca = request.form["dostawca"]
        print(nr_partii, zlecenie, zam, dostawca)
        pozycje = dane_zam_pianki_czasy(nr_partii)

        # print(pozycje)
        
        if zlecenie not in ["WOZKI DO DOSTAWY", "RAPORT MEMORY", "CZASY PROCESOW", "NAKLEJKI OWATY", "NAKLEJKI PIANKI"]:

            drukuj_raporty(nr_partii, zlecenie=zlecenie, pozycje=pozycje, zam=zam)

            return redirect(url_for('analiza_pianek.pobierz_raporty_do_zamowien', zlecenie=zlecenie, nr_partii=nr_partii.replace("/", "_")))
        
        elif zlecenie == "NAKLEJKI OWATY":
             
            naklejki_na_paczki_pianek(nr_partii,zam,True)

            return redirect(url_for('analiza_pianek.pobierz_raporty_do_zamowien', zlecenie=zlecenie, nr_partii=nr_partii.replace("/", "_")))

        elif zlecenie == "NAKLEJKI PIANKI":
             
            naklejki_na_paczki_pianek(nr_partii,zam,False)

            return redirect(url_for('analiza_pianek.pobierz_raporty_do_zamowien', zlecenie=zlecenie, nr_partii=nr_partii.replace("/", "_")))

        else:
            drukuj_raporty_xlsx(nr_partii, zlecenie, dostawca)

            return redirect(url_for('analiza_pianek.pobierz_raporty_do_zamowien', zlecenie=zlecenie, nr_partii=nr_partii.replace("/", "_"), dostawca=dostawca))

            
        
    
    return render_template("drukuj_raporty.html")
    
@analiza_pianek.route("/pobierz_raporty_do_zamowien/<zlecenie>/<nr_partii>", defaults={'dostawca': None})
@analiza_pianek.route("/pobierz_raporty_do_zamowien/<zlecenie>/<nr_partii>/<dostawca>")
def pobierz_raporty_do_zamowien(zlecenie, nr_partii, dostawca=None):
    print("send file:", zlecenie, nr_partii, dostawca)
    if dostawca:
        return send_file(f"../ZLECENIA_PROD/{zlecenie}/{nr_partii}/{dostawca}_{zlecenie}.xlsx")
    
    elif zlecenie == "NAKLEJKI OWATY":        
        return send_file(f"../ZLECENIA_PROD/NAKLEJKI OWATY/{nr_partii}.pdf")
    
    elif zlecenie == "NAKLEJKI PIANKI":        
        return send_file(f"../ZLECENIA_PROD/NAKLEJKI PIANKI/{nr_partii}.pdf")
    
    else:
        return send_file(f"../ZLECENIA_PROD/{zlecenie}/{nr_partii} {zlecenie}.pdf")