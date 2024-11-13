from flask import render_template, request, redirect, url_for
from Modele_db.modele_db import session
from sqlalchemy import text
from Pianki.Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as izp
from Pianki.Analiza_pianek.Podsumowanie_analizy_pianek import Podsumowanie_analizy_pianek
from Pianki.Analiza_pianek.funkcje_analizy_pianek import *

from Flask_server.Bluprints.analiza_pianek import analiza_pianek

from ..routes import *

ard = {x.MODEL: x for x in izp}
pap = Podsumowanie_analizy_pianek(izp)
z_pianki = dict()


@analiza_pianek.route("/")
def index():
    tabelka = Ogolna_analiza_objetosci("json")
    # br = Braki(WOLNE="SALDO")[0] #USUNAC PROBLEM Z DUBLUJACYMI SIE ZAMOWIANIAMI(JEDNO DOSTARCZONE DRUGIE W DRODZE TWORZĄ SIĘ DWIE POZYCJE)
    # zagr = Zagrozone(prt=False)

    # zagr_nie_zam = zagr[(zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0]

    # zagr_podsum = [f"WOLNE PONIZEJ MIN: {zagr.shape[0]} POZYCJE",
    # f"WOLNE PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE",
    # f"SALDO PONIZEJ MIN: {zagr[zagr.SALDO < zagr.MIN].shape[0]} POZYCJE",
    # f"SALDO PONIZEJ MIN NIE ZAMOWIONE: {zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0)&(zagr.SALDO < zagr.MIN)].shape[0]} POZYCJE"]
  

    return render_template("analiza_pianek.html", title="Analiza pianek",
                        #    zagrozone=zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0)&(zagr.SALDO < zagr.MIN)],
                        #    podsumowanie_zagrorzonych=zagr_podsum,
                        #    braki=br.sort_values(by=["GRUPA", "OPIS"]).drop("SALDO", axis=1).drop_duplicates("OPIS"), 
                           tabelka=tabelka)
    # return render_template("analiza_pianek.html", title="Analiza pianek")