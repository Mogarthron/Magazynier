from flask import Blueprint 


poduszki = Blueprint("poduszki", __name__, template_folder="templates/poduszki", static_folder="static")


from .routes import *
