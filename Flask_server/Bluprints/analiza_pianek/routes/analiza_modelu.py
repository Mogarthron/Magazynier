from ..routes import *

@analiza_pianek.route("/analiza_modelu/<model>", methods=["GET", "POST"])
def analiza_modelu(model):
    _model = pap[model]

    return render_template("analiza_modelu.html", tabelka_modelu=_model.ar) 
