from Pianki.Analiza_pianek import *
from Modele_db import engine, text
import pandas as pd
import fdb

import json

#@title PRZYGOTOWANIE DANYCH

#PLIKI ZAM_PIANKI
# komplety_pianek = pd.read_excel(zam_pianki_link, sheet_name="Arkusz3")
with engine.begin() as conn:
  komplety_pianek = pd.read_sql(text("SELECT * FROM KOMPLETY_PIANEK"), conn)
komplety_pianek['CZY_BRYLA'] = komplety_pianek['CZY_BRYLA'].fillna(1)
komplety_pianek['BRYLA_GEN'] = komplety_pianek['BRYLA_GEN'].fillna("").astype(str).apply(lambda x: x.replace(".", ","))
komplety_pianek["RODZINA_NAZWA"] = komplety_pianek.OPIS.apply(lambda x: x[:3])


with engine.begin() as conn:
  zam_pianki = pd.read_sql(text("""SELECT TYDZIEN, KOD, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY,
                      ZAM1, ZAM2, POTW_DATA_DOS_1 as dos1, POTW_DATA_DOS_2 as dos2, STATUS_KOMPLETACJA, UWAGI, nr_PZ from ZAM_PIANKI WHERE STATUS_KOMPLETACJA NOT LIKE '%ZAKONCZONO%' OR STATUS_KOMPLETACJA IS NULL"""), conn)


def dostarczone(zd, sk):
    """
    zd -> znacznik dostawcy
    sk -> status kompletacja

    0 - nie dostarczono lub dostarczono cześciowo (dostawca nie przywiózł wszystkich brył)
    1 - dostarczono częściowo (dodtarczył tylko jeden dostawca)
    2 - czeka na spakowanie
    3 - spakowana częściowo
    9999 - błąd
    """
    if type(sk) != str:
      return 0

    if sk == np.NaN:
      return 0

    if zd == np.NaN:
      return 0

    try:
      if len(zd) == len(sk):
        return 2
      elif sk == "":
        return 0
      else:
        return 1
    except:
      return 9999


zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']] = zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']].fillna("")

zam_pianki["dostarczono"] = zam_pianki.apply(lambda x: dostarczone(x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA), axis=1)


zam_nie_spakowane = zam_pianki[(zam_pianki.dostarczono == 2)]
zam_nie_spakowane.rename(columns={"ILE_ZAMOWIONE": "CZEKA_NA_SPAKOWANIE"}, inplace=True)
pianki_czesciowo_dostarczone = zam_pianki[(zam_pianki.dostarczono == 1)]
pianki_czesciowo_dostarczone.rename(columns={"ILE_ZAMOWIONE": "CZESIOWO_DOSTARCZONE"}, inplace=True)
pianki_w_drodze = zam_pianki[(zam_pianki.STATUS_KOMPLETACJA == "") & (~zam_pianki.ZNACZNIK_DOSTAWCY.isna())]
pianki_w_drodze.rename(columns={"ILE_ZAMOWIONE": "ZAMOWIONE"}, inplace=True)

#PLIK DANE_PIANKI_XXXX


def przygotowanie_danych_firebird(pda, data_ostaniej_paczki="2024.05.27"):
    with open("linki.json", "r") as c:
        param = json.load(c)["firebird"]

    con = fdb.connect(dsn=param["dns"], user=param["user"], password=param["password"], sql_dialect=param["sql_dialect"], fb_library_name=param["fb_library_name"])

    cur = con.cursor()

    cur.execute("SELECT megaraport_zewn.artykul_kod, megaraport_zewn.iledokwnzap FROM MEGARAPORT_ZEWN(202552, 0, 10, 50, '%WST%')")
    wstrzymane = pd.DataFrame(cur.fetchall(), columns=["KOD", "ILOSC"]) 

    NALICZONE_stmt = f"""
        SELECT NR_ZLECENIA, MAT_KOD AS KOD, ZAPOT_ZLEC, LIMIT_DATA_PROD FROM MATERIALY_NALICZONE_ZLEC('{data_ostaniej_paczki} 00:00:00', '2024.12.30 00:00:00', NULL, NULL, NULL, NULL, 1, 1, NULL, NULL, NULL) where mat_nazwa1 like '%KOMPLET PIANEK%'  AND STATUS_NS<60
        """

    SALDO_stmt = """SELECT Artykul.Artykul_Kod AS KOD, 
                        SUM( Mag_Dok_spec.ZNAK  * Mag_Dok_spec.ILOSC) AS SALDO 
                        FROM Mag_Dok_spec INNER JOIN ARTYKUL ON (Mag_Dok_spec.ARTYKUL_ID = Artykul.ARTYKUL_ID) 
                        INNER JOIN MAG_DOK_NAG ON (Mag_Dok_spec.MAG_DOK_NAG_ID = Mag_Dok_Nag.MAG_DOK_NAG_ID) 
                        INNER JOIN Magazyny ON Mag_dok_spec.magazyny_id = Magazyny.magazyny_id  
                    WHERE Mag_Dok_Nag.DATA <= cast('NOW' as timestamp) AND (MAG_DOK_SPEC.MAGAZYNY_ID=23) AND Artykul.Artykul_Kod LIKE '16.%' OR Artykul.Artykul_Kod LIKE '13.130%' GROUP BY Mag_Dok_spec.Magazyny_id, Artykul.Artykul_Kod, Artykul.Nazwa1,  
                        Magazyny.magazyny_kod, Artykul.stan_uruchamiajacy, Artykul.stan_MAX ORDER BY Magazyny.magazyny_kod"""

    cur.execute(SALDO_stmt)
    saldo = pd.DataFrame(cur.fetchall(), columns=["KOD", "SALDO"])    

    cur.execute(NALICZONE_stmt)
    naliczone = pd.DataFrame(cur.fetchall(), columns=["LIMIT_NAZWA", "KOD", "ZAPOT_ZLEC", "LIMIT_DATA_PROD"]).query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')")  
      
    
    con.close()    

    nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD").ZAPOT_ZLEC.sum().reset_index().rename(columns={"ZAPOT_ZLEC": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]

    return saldo, naliczone, wstrzymane, nal_paczki


def przygotowanie_danych_excel(pda):
    
    with open("./linki.json") as f:
        linki = json.load(f)
        path_dane_pianki = linki["path_dane_pianki"]

   

    saldo = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="SALDO", usecols="B,D,H")
    naliczone = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="NALICZONE", usecols="C,F,Y,Z,AK").query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')", engine='python')
    wstrzymane = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="ZLECENIA").drop_duplicates("KOD")#.query("KOD.str.contains('16.')", engine='python')

    #PACZKI Z ZAMÓWIENIAMI
    nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD_ART").ZAPOTRZ.sum().reset_index().rename(columns={"KOD_ART": "KOD", "ZAPOTRZ": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]

    naliczone = naliczone.rename(columns={'KOD_ART': "KOD", 'ZAPOTRZ': "ZAPOT_ZLEC"})

    return saldo, naliczone, wstrzymane, nal_paczki


saldo, naliczone, wstrzymane, nal_paczki = przygotowanie_danych_firebird(pda)

# saldo = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="SALDO", usecols="B,D,H")
# naliczone = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="NALICZONE", usecols="C,F,Y,Z,AK").query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')", engine='python')
# wstrzymane = pd.read_excel(path_dane_pianki+plik_DANE_PIANKI, sheet_name="ZLECENIA").drop_duplicates("KOD")#.query("KOD.str.contains('16.')", engine='python')


#PACZKI Z ZAMÓWIENIAMI
# nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD_ART").ZAPOTRZ.sum().reset_index().rename(columns={"KOD_ART": "KOD", "ZAPOTRZ": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]
