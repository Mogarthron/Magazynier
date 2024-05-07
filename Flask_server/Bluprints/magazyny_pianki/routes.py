from flask import render_template, request, redirect, url_for
from ..magazyny_pianki import magazyny_pianki


magazyny = {
    "MAGAZYN 1 ANTRESOLA 1": "",
    "MAGAZYN 1 ANTRESOLA 2": "",
    "MAGAZYN 2": "",
    "MAGAZYN 10": "",
    "MAGAZYN 11": ""
            }

@magazyny_pianki.route("/")
def index():

    magazyn_2 = list()


    return render_template("magazyny_pianki.html", title="MAGAZYNY PIANEK", magazyny=magazyny)