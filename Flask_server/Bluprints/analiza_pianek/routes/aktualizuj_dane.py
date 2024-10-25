from ..routes import *


from Modele_db import engine, text
from Modele_db.modele_db import ZAM_PIANKI, session
import pandas as pd
import fdb
from datetime import datetime as dt, timedelta 
import json


# with open("./linki.json") as f:
#   linki = json.load(f)
#   path_dane_pianki = linki["path_dane_pianki"]

with open("daty_kompletacji.json") as f:
    dkom = json.load(f)
    daty_kompletacji = dkom["daty_kompletacji"]
    daty_kompletacji = dkom["daty_kompletacji"]
    data_wstawienia_pierszej_kompletacji = dkom["data_wstawienia_pierwszej_kompletacji"]

for k in daty_kompletacji:
    daty_kompletacji[k] = dt.strptime(daty_kompletacji[k], "%Y-%m-%d")

pda = list(daty_kompletacji.keys())


def aktualizuj_zamowienia(pda:list, data_pierwszej_paczki:str="2024.06.03"):
  """
  pda -> lista numerów paczek np ['31/01', '32/01']
  data_pierwszej_paczki -> data 'poniedziałku' pierwszej paczki z pda
  """
  with open("linki.json", "r") as c:
        param = json.load(c)["firebird"]

  con = fdb.connect(dsn=param["dns"], user=param["user"], password=param["password"], sql_dialect=param["sql_dialect"], fb_library_name=param["fb_library_name"])

  cur = con.cursor()

  cur.execute("SELECT megaraport_zewn.artykul_kod, megaraport_zewn.iledokwnzap FROM MEGARAPORT_ZEWN(202552, 0, 10, 50, '%WST%')")
  wstrzymane = pd.DataFrame(cur.fetchall(), columns=["KOD", "ILOSC"]) 

  NALICZONE_stmt = f"""
        SELECT NR_ZLECENIA, MAT_KOD AS KOD, ZAPOT_ZLEC, LIMIT_DATA_PROD FROM MATERIALY_NALICZONE_ZLEC('{data_pierwszej_paczki} 00:00:00', '2024.12.30 00:00:00', NULL, NULL, NULL, NULL, 1, 1, NULL, NULL, NULL) 
        where mat_nazwa1 like '%KOMPLET PIANEK%'  AND STATUS_NS<60
        """

  cur.execute(NALICZONE_stmt)
  naliczone = pd.DataFrame(cur.fetchall(), columns=["LIMIT_NAZWA", "KOD", "ZAPOT_ZLEC", "LIMIT_DATA_PROD"]).query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')")  
    
  con.close()    

  with engine.begin() as conn:    
    naliczone.rename(columns={'LIMIT_NAZWA':"limit_nazwa", 'KOD':"kod", 'ZAPOT_ZLEC':"zapot_zlec", 'LIMIT_DATA_PROD':"limit_data_prod"}).to_sql("NALICZONE", conn, if_exists="replace")
    wstrzymane.rename(columns={"KOD":"kod", 'ILOSC':"ilosc"}).to_sql("WSTRZYMANE", conn, if_exists="replace")

  # nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD").ZAPOT_ZLEC.sum().reset_index().rename(columns={"ZAPOT_ZLEC": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]


def aktualizuj_saldo():
  with open("linki.json", "r") as c:
      param = json.load(c)["firebird"]

  con = fdb.connect(dsn=param["dns"], user=param["user"], password=param["password"], sql_dialect=param["sql_dialect"], fb_library_name=param["fb_library_name"])

  cur = con.cursor()
  
  SALDO_stmt = """SELECT Artykul.Artykul_Kod AS KOD, 
                        --Artykul.Nazwa1
                        SUM( Mag_Dok_spec.ZNAK  * Mag_Dok_spec.ILOSC) AS SALDO 
                        FROM Mag_Dok_spec INNER JOIN ARTYKUL ON (Mag_Dok_spec.ARTYKUL_ID = Artykul.ARTYKUL_ID) 
                        INNER JOIN MAG_DOK_NAG ON (Mag_Dok_spec.MAG_DOK_NAG_ID = Mag_Dok_Nag.MAG_DOK_NAG_ID) 
                        INNER JOIN Magazyny ON Mag_dok_spec.magazyny_id = Magazyny.magazyny_id  
                    WHERE Mag_Dok_Nag.DATA <= cast('NOW' as timestamp) 
                    AND (MAG_DOK_SPEC.MAGAZYNY_ID=23) 
                    AND Artykul.Artykul_Kod LIKE '16.%' OR Artykul.Artykul_Kod LIKE '13.130%' 
                    GROUP BY Mag_Dok_spec.Magazyny_id, Artykul.Artykul_Kod, Artykul.Nazwa1,  
                        Magazyny.magazyny_kod, Artykul.stan_uruchamiajacy, Artykul.stan_MAX ORDER BY Magazyny.magazyny_kod"""

  cur.execute(SALDO_stmt)
  saldo = pd.DataFrame(cur.fetchall(), columns=["KOD", "SALDO"])          
    
  con.close()    
  with engine.begin() as conn:
    saldo.rename(columns={"KOD": "kod", "SALDO": "stan"}).to_sql("SALDO", conn, if_exists="replace")


@analiza_pianek.route("/aktualizuj_dane", methods=["GET", "POST"])
def aktualizuj_dane():    

    if request.method == "POST":
        print(list(request.form.keys()))
        if "pobierz_naliczone_i_wsztrzymane" in list(request.form.keys()):
            aktualizuj_zamowienia(pda, data_wstawienia_pierszej_kompletacji)

        if "aktualizuj_saldo" in list(request.form.keys()):
           aktualizuj_saldo()

    return render_template("aktualizuj_dane.html")