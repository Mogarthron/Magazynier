from flask import render_template, request, redirect, url_for
from ..magazyny_pianki import magazyny_pianki


@magazyny_pianki.route("/")
def index():
    return render_template("magazyny_pianki.html", title="Magazyn 2")