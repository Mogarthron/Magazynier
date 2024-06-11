from ..routes import *


@wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
def plan_pracy():

    plan_pracy = session.query(ZAM_PIANKI).filter(
                    or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
    
    json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))

    if request.method == "POST":
        if "zakonczono" in list(request.form.keys())[0]:
            print("zakonczono id", int(list(request.form.keys())[0].replace("zakonczono_", "")))
            
        if "edytuj" in list(request.form.keys())[0]:
            print("edytuj id", int(list(request.form.keys())[0].replace("edytuj_", "")))

        if "leniwa" == list(request.form.keys())[0].split("_")[0]:
            print("leniwa id", int(list(request.form.keys())[0].replace("leniwa_", "")))

        if "leniwaSkos" == list(request.form.keys())[0].split("_")[0]:
            print("leniwaSkos id", int(list(request.form.keys())[0].replace("leniwaSkos_", "")))

        if "owatyWydane" in list(request.form.keys())[0].split("_")[0]:
            print("owatyWydane id", int(list(request.form.keys())[0].replace("owatyWydane_", "")))

        if "owatyWyciete" in list(request.form.keys())[0].split("_")[0]:
            print("owatyWyciete id", int(list(request.form.keys())[0].replace("owatyWyciete_", "")))

        if "owatyKompletacja" in list(request.form.keys())[0].split("_")[0]:
            print("owatyKompletacja id", int(list(request.form.keys())[0].replace("owatyKompletacja_", "")))

        if "kj" in list(request.form.keys())[0].split("_")[0]:
            # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
            return redirect(url_for("wydzial_pianek.raport_jakosciowy", id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("plan_pracy.html", title="PLAN PRACY", plan_pracy={"plan_pracy":json_plan_pracy})