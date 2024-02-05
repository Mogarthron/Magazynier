from flask import Flask, render_template, request, url_for, flash, redirect
from pianki import graphJSON, dos, lista_bryl
import sqlite3

# cnn = sqlite3.connect("mydb.db")
# cur = cnn.execute("select nazwa_magazynu from Magazyn")
# magazyny = [x[0] for x in cur.fetchall()]








zam_pianki = list()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")#, magazyny = magazyny)    


# @app.route("/magazyn/<mag>")
# def magazyn(mag=None):        
#     return render_template("magazyn.html", mag=magazyny[mag])

@app.route("/mag1")
def mag1():
    return "Magazyn 1"

@app.route("/dodaj_pianki_model", methods=["POST","GET"])
def dodaj_pianki_model():
    
    lista_modeli = list(lista_bryl.keys())
    
    if request.method == "POST" and "model" in request.form:
        # print(request.form["model"])
        return redirect(url_for("dodaj_pianki_bryla", model=request.form["model"]))

    if request.method == "POST" and "wyczysc_bryly" in request.form:
        # print("WYCZYSC")
        zam_pianki.clear()
        return render_template("dodaj_pianki_model.html", lista_modeli=lista_modeli, zam_pianki=zam_pianki)
    

    
    if request.method == "POST":# and "del_" in request.form:
        odpowiedz =list(request.form.keys())[0] 
        usun_bryle = ""
        edytuj_bryle = ""
        if "del_" in odpowiedz: 
            # zam_pianki = [x for x in zam_pianki if odpowiedz.split("_")[1:] != x[:2]]
            # print(odpowiedz.split("_")[1:], zam_pianki)
            pass
            

    return render_template("dodaj_pianki_model.html", lista_modeli=lista_modeli, zam_pianki=enumerate(zam_pianki))

@app.route("/dodaj_pianki_bryla/<model>", methods=["POST", "GET"])
def dodaj_pianki_bryla(model):

    bryly = list()
    ile = list()
    if request.method == "POST":
        bryly = request.form.getlist("bryla")
        ile = request.form.getlist("ile")
        
    
    for i in range(len(bryly)):
        if ile[i] != "":
            zam_pianki.append([model, bryly[i], ile[i]])

    if request.method == "POST":
        # print(request.form["bryla"])
        return redirect(url_for("dodaj_pianki_model"))


    return render_template("dodaj_pianki_bryla.html", model=model, bryla=lista_bryl[model])

@app.route("/dostawy_pianek")
def dostawy_pianek():

    return render_template("dostawy_pianek.html", graphJSON=graphJSON, dostawy=dos[["NR_Dostawy", "Dostawca", "Data_Dostawy", "Opis"]])




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

