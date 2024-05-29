from ..routes import *

@analiza_pianek.route("/zapis_do_bazy/<nr_partii>", methods=["GET", "POST"])
def zapis_do_bazy(nr_partii):
    

    return render_template("zapis_do_bazy.html", nr_partii=nr_partii)