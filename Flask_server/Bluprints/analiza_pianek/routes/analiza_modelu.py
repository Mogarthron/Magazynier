from ..routes import *




import plotly
import json

@analiza_pianek.route("/analiza_modelu/<model>", methods=["GET", "POST"])
def analiza_modelu(model):

    _model = pap[model]
    ar = _model.ar
    ar[ar.columns[1:]] = ar[ar.columns[1:]].astype(int)

    return render_template("analiza_modelu.html", tabelka_modelu=ar, 
                           graphJSON_Saldo=json.dumps(_model.Wykres_obj(nazwa_modelu=False, show_fig=False), cls=plotly.utils.PlotlyJSONEncoder),
                           graphJSON_Wolne=json.dumps(_model.Wykres_obj(nazwa_modelu=False, saldo=False, show_fig=False), cls=plotly.utils.PlotlyJSONEncoder)) 
