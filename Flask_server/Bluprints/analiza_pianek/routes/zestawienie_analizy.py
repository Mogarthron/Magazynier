from . import *




@analiza_pianek.route("/zestawienie_analizy", methods=["GET", "POST"])
def zestawienie_analizy():   

    return render_template("zestawienie_analizy.html", title="Zestawienie Analizy", pap=pap)