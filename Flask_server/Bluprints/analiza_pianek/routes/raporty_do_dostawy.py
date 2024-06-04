from ..routes import *






@analiza_pianek.route("/raporty", methods=["GET", "POST"])
def raporty():   
    return render_template("raporty_do_dostawy.html")
    