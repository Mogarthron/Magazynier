from ..routes import *
from Flask_server.Bluprints.wydzial_pianek.tabela_dostaw_pianek import tabelka_dostawy_pianek, df
from Pianki.Dostawy_pianek import wykers_zapelnienia_samochodow

# import plotly.express as px
import plotly
import json


@wydzial_pianek.route("/dostawy_pianek")
def dostawy_pianek():
       
    fig = wykers_zapelnienia_samochodow(df)
    
    return render_template("dostawy_pianek.html", title="Dostawy pianek", 
                                                  tabelka_dostawy_pianek=tabelka_dostawy_pianek,  
                                                  graphJSON=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))