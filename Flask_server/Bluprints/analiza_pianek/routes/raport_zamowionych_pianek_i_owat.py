from ..routes import *

from Pianki.Raporty_do_zamowien.Komponowanie_zamowienia import Raport_zamowionych_pianek_i_owat
import json
import os
from datetime import datetime as dt

@analiza_pianek.route("/raport_zamowionych_pianek_i_owat", defaults={"nr_partii": None})
@analiza_pianek.route("/raport_zamowionych_pianek_i_owat/<nr_partii>")
def raport_zamowionych_pianek_i_owat(nr_partii):
    
    
    if os.path.exists("./propozycja_zamowionych_pianek.json") and nr_partii:
        nr_partii = nr_partii.replace("_", "/")

        with open("./propozycja_zamowionych_pianek.json", "r") as f:
            propozecje_zam = json.load(f)[nr_partii]
    

        data_zamowienia = dt.now().strftime("%Y-%m-%d")
        nr_zamowienia = propozecje_zam["NR_ZAM"]
        preferowana_data_dostawy = propozecje_zam["DATA_DOS"]
        dostawca = propozecje_zam["DOSTAWCA"]
   
        cls_list = list()
        zestawienie_list = list()
        for k in propozecje_zam["PROP_ZAM"]:
            zmod, cls = ard[k].Bryly_do_zamowienia(korekta_zam=propozecje_zam["PROP_ZAM"][k])

            cls_list.append(cls)
            zestawienie_list.append(zmod)

        for i in zestawienie_list:
            print(i.columns)

        df, rolki_owaty = Raport_zamowionych_pianek_i_owat(zestawienie_list)

        tabelka = [
        [x[1], x[2], f"{x[3]:.0f}", f"{x[4]:.0f}", f"{x[5]:.0f}", f"{x[6]:.0f}", f"{x[7]:.0f}", f"{x[8]:.0f}"] 
        for x in df.itertuples()]

        mb = [f"{df.ZIELONA.sum():.0f}", f"{df.NIEBIESKA.sum():.0f}", f"{df.CZERWONA.sum():.0f}", f"{df['ŻÓŁTA'].sum():.0f}", f"{df.W3.sum():.0f}"]
        
        obietosc_zam = {"VITA": 0,
                        "CIECH": 0,
                        "PIANPOL": 0,
                        "OLTA": 0}
        for cls in cls_list:
            obietosc_zam += cls

        return render_template("raport_zamowionych_pianek_i_owat.html", title=f"ZAM PIANPOL {data_zamowienia}", 
                                                                        dostawca=dostawca, data_zamowienia=data_zamowienia,                                                                        
                                                                        tabelka=tabelka, nr_partii=nr_partii, nr_zamowienia=nr_zamowienia, 
                                                                        preferowana_data_dostawy=preferowana_data_dostawy, mb=mb, rolki_owaty=rolki_owaty, 
                                                                        obietosc_zam = obietosc_zam)
    
    return render_template("raport_zamowionych_pianek_i_owat.html", title=f"PROPOZYCJA ZAMOWIENIA", tabelka=None)