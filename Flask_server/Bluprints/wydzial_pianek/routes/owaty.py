from ..routes import *
from datetime import datetime as dt
from sqlalchemy import and_
from Modele_db.modele_db import ZAM_PIANKI, OWATY, session
import pandas as pd


def aktualizuj_owaty():

    owaty_w_toku = pd.DataFrame(session.query(ZAM_PIANKI.nr_partii, ZAM_PIANKI.opis, ZAM_PIANKI.ile_zam).filter(
                        ZAM_PIANKI.owaty_kompletacja == None, ZAM_PIANKI.data_zakonczenia == None).all(),
                columns=["NR_PARTII", "OPIS", "ILE_ZAM"]).merge(
        pd.pivot_table(pd.DataFrame(session.query(OWATY.OPIS, OWATY.TYP_OWATY, OWATY.ZUZYCIE).all()), values="ZUZYCIE", columns="TYP_OWATY", index="OPIS", fill_value=0),
        how="left",
        on="OPIS"
    ).dropna(axis=0)

    owaty_w_toku["L1"] = owaty_w_toku.L1 * owaty_w_toku.ILE_ZAM * 1.1 
    owaty_w_toku["O1"] = owaty_w_toku.O1 * owaty_w_toku.ILE_ZAM * 1.1   
    owaty_w_toku["O2"] = owaty_w_toku.O2 * owaty_w_toku.ILE_ZAM * 1.1   
    owaty_w_toku["O3"] = owaty_w_toku.O3 * owaty_w_toku.ILE_ZAM * 1.1   
    owaty_w_toku["W3"] = owaty_w_toku.W3 * owaty_w_toku.ILE_ZAM * 1.1 
            
    ozn_owat = {                  #g/m2, szer, mb
        "O1": ["B/16/150 (1.6x50)", 150, 1.6, 50, "zielona", "73.115.00001"],
        "O2": ["B/16/200 (1.2x40)", 200, 1.2, 40, "niebieska", "73.120.00001"],
        "O3": ["B/16/200 (1.6x40)", 200, 1.6, 40, "czerwona", "73.120.00002"],
    }

    owaty_podsumowanie = owaty_w_toku.iloc[:,3:].sum()
    owaty_Rolki = pd.Series({"L1": 60, 
                             "O1": 50, 
                             "O2": 40, 
                             "O3": 40, 
                             "W3": 1000})

    owaty = pd.DataFrame([owaty_podsumowanie, owaty_Rolki]).T
    owaty.columns = ["ZAPOTRZ", "ROLKI"]
    owaty["ILE ROLEK ZPOTRZ"] = owaty.ZAPOTRZ / owaty.ROLKI
    
    owaty_w_toku[owaty_w_toku.columns[2:]] = owaty_w_toku[owaty_w_toku.columns[2:]].astype(int)

    return owaty.astype(int), owaty_w_toku


@wydzial_pianek.route("/owaty", methods=["GET", "POST"])
def owaty(): 

    owaty, owaty_w_toku = aktualizuj_owaty()

    if request.method == "POST":
       nr_partii, opis = list(request.form.keys())[0].split("|")
       poz = session.query(ZAM_PIANKI).filter(
            ZAM_PIANKI.nr_partii == nr_partii, ZAM_PIANKI.opis == opis).first()           
       poz.owaty_kompletacja = dt.date(dt.now())
       session.commit()

       return redirect(url_for("wydzial_pianek.owaty", title="OWATY", owaty=aktualizuj_owaty()[0], owaty_w_toku=aktualizuj_owaty()[1]))
       
    return render_template("owaty.html", title="OWATY", owaty=owaty, owaty_w_toku=owaty_w_toku)