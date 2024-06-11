from ..routes import *

@wydzial_pianek.route("/przyjecie_dostawy/<nr_samochodu>", methods=["GET", "POST"])
def przyjecie_dostawy(nr_samochodu):
    
    pianki_w_drodze = session.query(ZAM_PIANKI).filter(ZAM_PIANKI.nr_samochodu.like(f"%{nr_samochodu}%")).all()
    
    json_pianki_w_drodze = list(map(lambda x: x.pianki_w_drodze_to_json(), pianki_w_drodze))
    
    raport_realizacji_dostawy = [
        ["ADAM RZEPKO", 57, 190, 0, 0, 0],
        ["PIOTR ŁUPIŃSKI", 57, 0, 0, 305, 225],
        ["PAWEŁ MIŚKO", 57, 0, 0, 165, 225],
    ]

    if request.method == "POST" and "kj" in list(request.form.keys())[0].split("_")[0]:
        # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
        return redirect(url_for("wydzial_pianek.raport_jakosciowy", nr_samochodu=nr_samochodu ,id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("przyjecie_dostawy.html", title=f"Przyjecie dostawy {nr_samochodu}", 
                                                        nr_samochodu=nr_samochodu, 
                                                        raport_realizacji_dostawy=raport_realizacji_dostawy,
                                                        pianki_w_drodze={"pianki_w_drodze":json_pianki_w_drodze})