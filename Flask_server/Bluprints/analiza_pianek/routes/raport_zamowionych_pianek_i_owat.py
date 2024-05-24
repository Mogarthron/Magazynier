from ..routes import *

from Pianki.Raporty_do_zamowien.Komponowanie_zamowienia import Raport_zamowionych_pianek_i_owat

@analiza_pianek.route("/raport_zamowionych_pianek_i_owat")
def raport_zamowionych_pianek_i_owat():

    nr_partii = "20/01"
    data_zamowienia = "2024-05-24"
    nr_zamowienia = "24/0516"
    preferowana_data_dostawy = "2024-06-21"

    # tabelka = [
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
    #     ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0]
    # ]
    cls_list = list()
    zestawienie_list = list()
    for k in z_pianki:
        zmod, cls = ard[k].Bryly_do_zamowienia(korekta_zam=z_pianki[k])

        cls_list.append(cls)
        zestawienie_list.append(zmod)

    for i in zestawienie_list:
        print(i.columns)

    df, rolki_owaty = Raport_zamowionych_pianek_i_owat(zestawienie_list)

    tabelka = [
    [x[1], x[2], f"{x[3]:.0f}", f"{x[4]:.0f}", f"{x[5]:.0f}", f"{x[6]:.0f}", f"{x[7]:.0f}", f"{x[8]:.0f}"] 
    for x in df.itertuples()]

    mb = [f"{df.ZIELONA.sum():.0f}", f"{df.NIEBIESKA.sum():.0f}", f"{df.CZERWONA.sum():.0f}", f"{df['ŻÓŁTA'].sum():.0f}", f"{df.W3.sum():0f}"]
    

    
    return render_template("raport_zamowionych_pianek_i_owat.html", title=f"ZAM PIANPOL {data_zamowienia}", tabelka=tabelka, nr_partii=nr_partii, nr_zamowienia=nr_zamowienia, preferowana_data_dostawy=preferowana_data_dostawy, mb=mb, rolki_owaty=rolki_owaty)