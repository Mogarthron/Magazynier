from flask import Blueprint 


wydzial_pianek = Blueprint("wydzial_pianek", __name__, template_folder="templates/wydzial_pianek", static_folder="static")


from ..wydzial_pianek.routes import *
