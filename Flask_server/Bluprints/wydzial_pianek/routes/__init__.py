from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session, ZAM_PIANKI, RAPORT_KJ_DO_DOSTAWY_PIANEK#, AKTYWNE_DOSTAWY 
from Modele_db import engine
from sqlalchemy import or_, text

from Pianki.Dostawy_pianek import wykers_zapelnienia_samochodow#, obietosci_samochodow




from Flask_server.Bluprints.wydzial_pianek import wydzial_pianek
from ..routes import *

@wydzial_pianek.route("/")
def index():   

    return render_template("wydzial_pianek.html", title="Wydział pianek")


@wydzial_pianek.route("/naklejki")
def naklejki():

    with engine.begin() as conn:
        zp = conn.execute(text(f"""SELECT MODEL, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE,
                        NR_PARTII from ZAM_PIANKI WHERE ZAM1 in('24/0486') --AND OPIS NOT LIKE '%AVANT%'"""))
    
    zam_pianki = zp.fetchall()

    wiersze = list()

    for row in zam_pianki:
        
        for i in range(row[3]):
            
            wiersze.append([row[4], row[1], f"{i+1}/{row[3]}", row[0], row[2].replace(row[0], "").strip()])
          

    return render_template("naklejki_na_paczki_pianek_zebra.html", wiersze=wiersze)
