from flask import Flask, render_template, request, url_for, flash, redirect
from Analiza_pianek import Podsumowanie_analizy_pianek
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol

arp = Podsumowanie_analizy_pianek(instrukcja_zamawiania_pianpol)

app = Flask(__name__)

@app.route("/")
def index():

    return render_template("index.html", tables=[arp.Tabela_podsumowania_analizy.to_html(index=False, classes='table table-striped table-hover', header="true")])#, magazyny = magazyny)    






if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

