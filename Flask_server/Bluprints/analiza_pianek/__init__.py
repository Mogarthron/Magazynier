from flask import Blueprint

analiza_pianek = Blueprint("analiza_pianek", __name__, template_folder="templates/analiza_pianek", static_folder="static")

from ..analiza_pianek.routes import index, dokumentacja_pianek, raport_zamowionych_pianek_i_owat, dodaj_pianki_model, dodaj_pianki_bryla, zapis_do_bazy, analiza_modelu, zestawienie_analizy, drukuj_raporty, aktualizuj_dane, braki, ponizej_stanu_min
from ..analiza_pianek.routes.raporty_do_dostawy import *