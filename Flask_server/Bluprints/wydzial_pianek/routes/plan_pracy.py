from ..routes import *
from datetime import datetime as dt
from sqlalchemy import and_

def zaladuj_plan_pracy():

    # plan_pracy = session.query(ZAM_PIANKI).filter(
    #                 # or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
   
    plan_pracy = session.query(ZAM_PIANKI).filter(
        and_(
            or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None),
            ZAM_PIANKI.status_kompletacja != ''
        )
    ).all()

    
    json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))

    return json_plan_pracy

@wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
def plan_pracy():

    # plan_pracy = session.query(ZAM_PIANKI).filter(
    #                 or_(ZAM_PIANKI.status_kompletacja.not_like("%ZAKONCZONO%"), ZAM_PIANKI.status_kompletacja == None)).all()
    
    json_plan_pracy = zaladuj_plan_pracy()

    if request.method == "POST":
        if "zakonczono" in list(request.form.keys())[0]:

            id_zam_pianki = int(list(request.form.keys())[0].replace("zakonczono_", ""))
            poz = session.query(ZAM_PIANKI).get(id_zam_pianki)
            poz.status_kompletacja = f"ZAKONCZONO"
            poz.data_zakonczenia = dt.date(dt.now())
            session.commit()
            
            return redirect(url_for("wydzial_pianek.plan_pracy", title="PLAN PRACY", plan_pracy=zaladuj_plan_pracy()))
            # return render_template("plan_pracy.html", title="PLAN PRACY", plan_pracy=zaladuj_plan_pracy())
        
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