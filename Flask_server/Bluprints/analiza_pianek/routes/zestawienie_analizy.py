from . import *
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Pianki.Analiza_pianek.Podsumowanie_analizy_pianek import Podsumowanie_analizy_pianek
# ard = {x.MODEL: x for x in izp}


@analiza_pianek.route("/zestawienie_analizy", methods=["GET", "POST"])
def zestawienie_analizy():   
    pap = Podsumowanie_analizy_pianek(izp)
    return render_template("zestawienie_analizy.html", title="Zestawienie Analizy", pap=pap)