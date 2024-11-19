from ..routes import *
from datetime import datetime as dt
from sqlalchemy import and_

def zaladuj_plan_pracy():
        
    plan_pracy = session.query(ZAM_PIANKI).filter(ZAM_PIANKI.data_zakonczenia == None).all()
    
    json_plan_pracy = list(map(lambda x: x.plan_pracy_to_json(), plan_pracy))

    return json_plan_pracy

@wydzial_pianek.route("/plan_pracy", methods=["GET", "POST"])
def plan_pracy():
   
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
                       

        if "zatwierdzDostawe" in list(request.form.keys()):
            print(list(request.form.keys()))
            print("zatwierdzDostawe id", list(request.form.keys())[0].split("_")[-1])
            print("Status:", request.form[list(request.form.keys())[0]])

            id_zam_pianki = int(list(request.form.keys())[0].split("_")[-1])
            poz = session.query(ZAM_PIANKI).get(id_zam_pianki)           
            poz.status_kompletacja = request.form[list(request.form.keys())[0]]
            session.commit()

            return redirect(url_for("wydzial_pianek.plan_pracy", title="PLAN PRACY", plan_pracy=zaladuj_plan_pracy()))

        if "owatyKompletacja" in list(request.form.keys())[0].split("_")[0]:
            print("owatyKompletacja id", int(list(request.form.keys())[0].replace("owatyKompletacja_", "")))

            id_zam_pianki = int(list(request.form.keys())[0].replace("owatyKompletacja_", ""))
            poz = session.query(ZAM_PIANKI).get(id_zam_pianki)           
            poz.owaty_kompletacja = dt.date(dt.now())
            session.commit()

            return redirect(url_for("wydzial_pianek.plan_pracy", title="PLAN PRACY", plan_pracy=zaladuj_plan_pracy()))

        # if "kj" in list(request.form.keys())[0].split("_")[0]:
        #     # print("kj id", int(list(request.form.keys())[0].replace("kj_", "")))
        #     return redirect(url_for("wydzial_pianek.raport_jakosciowy", id=int(list(request.form.keys())[0].replace("kj_", ""))))

    return render_template("plan_pracy.html", title="PLAN PRACY", plan_pracy={"plan_pracy":json_plan_pracy})