from ..routes import *
from Pianki.Raporty_do_zamowien.raporty_do_zamowien import dane_zam_pianki_czasy, drukuj_raporty
from flask import send_file

@analiza_pianek.route("/raporty_do_zamowien", methods=["GET", "POST"])
def raporty_do_zamowien():
    
    if request.method == "POST":
        nr_partii = request.form["nr_partii"]
        zlecenie = request.form["typ_zlecenia"]
        zam = request.form["zam"]
        print(nr_partii, zlecenie, zam)
        pozycje = dane_zam_pianki_czasy(nr_partii)

        print(pozycje)

        drukuj_raporty(nr_partii, zlecenie=zlecenie, pozycje=pozycje, zam=zam)

        return redirect(url_for('analiza_pianek.pobierz_raporty_do_zamowien', zlecenie=zlecenie, nr_partii=nr_partii.replace("/", "_")))    
        
    
    return render_template("drukuj_raporty.html")
    
@analiza_pianek.route("/pobierz_raporty_do_zamowien/<zlecenie>/<nr_partii>")
def pobierz_raporty_do_zamowien(zlecenie, nr_partii):

    return send_file(f"../ZLECENIA_PROD/{zlecenie}/{nr_partii} {zlecenie}.pdf")