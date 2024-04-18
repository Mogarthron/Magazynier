from flask import Blueprint

analiza_pianek = Blueprint("analiza_pianek", __name__, template_folder="templates/analiza_pianek")

from ..analiza_pianek import routes