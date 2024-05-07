from flask import render_template, request, redirect, url_for
from ..magazyny_pianki import magazyny_pianki


magazyny = {
    "A": {"nazwa": "MAGAZYN 1 - ANTRESOLA 1"},
    "B": {"nazwa": "MAGAZYN 1 - ANTRESOLA 2"},
    # "MAGAZYN 2": {"skr":"C", },
    # "MAGAZYN 10": {"skr":"D", },
    # "MAGAZYN 11": {"skr":"E", }
            }

@magazyny_pianki.route("/")
def index():

    return render_template("magazyny_pianki.html", title="MAGAZYNY PIANEK", magazyny=magazyny)

@magazyny_pianki.route("/magazyn/<ozn_mag>")
def magazyn(ozn_mag):

    pass