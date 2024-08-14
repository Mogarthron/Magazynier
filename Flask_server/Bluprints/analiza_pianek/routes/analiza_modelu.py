from ..routes import *




import plotly
import json

@analiza_pianek.route("/analiza_modelu/<model>", methods=["GET", "POST"])
def analiza_modelu(model):
    _model = pap[model]

    return render_template("analiza_modelu.html", tabelka_modelu=_model.ar, graphJSON=json.dumps(_model.Wykres_obj(nazwa_modelu=False, show_fig=False), cls=plotly.utils.PlotlyJSONEncoder)) 
