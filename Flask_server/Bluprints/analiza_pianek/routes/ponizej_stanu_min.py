from flask import render_template
from Pianki.Analiza_pianek.funkcje_analizy_pianek import *
from ..routes import *


@analiza_pianek.route("/ponizej_stanu_min")
def ponizej_stanu_min():
    zagr = Zagrozone(prt=False)

   #  zagr_nie_zam = zagr[(zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0]
    zagr_nie_zam = zagr[(zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE + zagr.CZESIOWO_DOSTARCZONE) == 0]

    zagr_podsum = [f"WOLNE PONIZEJ MIN: {zagr.shape[0]} POZYCJE",
    f"WOLNE PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE",
    f"SALDO PONIZEJ MIN: {zagr[zagr.SALDO < zagr.MIN].shape[0]} POZYCJE",
    f"SALDO PONIZEJ MIN NIE ZAMOWIONE: {zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE + zagr.CZESIOWO_DOSTARCZONE) == 0)&(zagr.SALDO < zagr.MIN)].shape[0]} POZYCJE"]
  

    return render_template("ponizej_stanu_min.html", 
                           title="Ponizej satnu",
                        #    zagrozone=zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0)&(zagr.SALDO < zagr.MIN)],
                           zagrozone=zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE + zagr.CZESIOWO_DOSTARCZONE) == 0)],
                           podsumowanie_zagrorzonych=zagr_podsum
                          
                           )