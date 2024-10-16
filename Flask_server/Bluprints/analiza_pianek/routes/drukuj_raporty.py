from ..routes import *
from Pianki.Raporty_do_zamowien.raporty_do_zamowien import dane_zam_pianki_czasy, drukuj_raporty
from flask import send_file

@analiza_pianek.route("/drukuj_raporty_do_zamowien/<nr_tygodnia>/<zlecenie>/<zam>", methods=["GET", "POST"])
def drukuj_raporty_do_zamowien(nr_tygodnia, zlecenie, zam):
    
    

    pozycje = dane_zam_pianki_czasy(int(nr_tygodnia))
    
    drukuj_raporty(nr_tygodnia, zlecenie=zlecenie, zam=zam, pozycje=pozycje)
            
    return send_file(f"../ZLECENIA_PROD/{zlecenie}/{nr_tygodnia} {zlecenie}.pdf")
    