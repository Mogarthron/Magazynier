from flask import Blueprint 


magazyny_pianki = Blueprint("magazyny_pianki", __name__, template_folder="templates/magazyny_pianki", static_folder="static")


from ..magazyny_pianki.routes import *