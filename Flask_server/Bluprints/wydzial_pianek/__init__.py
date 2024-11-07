from flask import Blueprint 


wydzial_pianek = Blueprint("wydzial_pianek", __name__, template_folder="templates/wydzial_pianek", static_folder="static")


from ..wydzial_pianek.routes import index, naklejki, dostawy_pianek, plan_pracy, raport_jakosciowy, przyjecie_dostawy, owaty