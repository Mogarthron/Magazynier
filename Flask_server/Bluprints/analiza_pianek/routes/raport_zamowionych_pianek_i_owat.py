from ..routes import *

@analiza_pianek.route("/raport_zamowionych_pianek_i_owat")
def raport_zamowionych_pianek_i_owat():

    nr_partii = "20/01"
    data_zamowienia = "2024-05-15"
    nr_zamowienia = "24/0516"
    preferowana_data_dostawy = "2024-06-21"

    tabelka = [
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0],
        ["16.077.15200.60", "SAMOA 1,5z", 70, 131, 122, 0, 0 ,0]
    ]


    
    return render_template("raport_zamowionych_pianek_i_owat.html", tabelka=tabelka)