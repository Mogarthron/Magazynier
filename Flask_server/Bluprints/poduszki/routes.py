from flask import render_template, request, redirect, url_for
from ..poduszki import poduszki

@poduszki.route("/")
def index():

    return render_template("poduszki.html", title="Poduszki")