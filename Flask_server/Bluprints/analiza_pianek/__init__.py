from flask import Blueprint

analiza_pianek = Blueprint("analiza_pianek", __name__, template_folder="templates/analiza_pianek")

from ..analiza_pianek.routes import index, dokumentacja_pianek, raport_zamowionych_pianek_i_owat, dodaj_pianki_model, dodaj_pianki_bryla, zapis_do_bazy