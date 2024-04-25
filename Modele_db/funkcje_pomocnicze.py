from Modele_db import engine, text
from Modele_db.modele_db import *
import pandas as pd


with engine.begin() as conn:
    pz = pd.read_sql(text("SELECT * FROM PRZYJECIE_ZEWNETRZNE"), conn)
    pz_poz = pd.read_sql(text("SELECT * FROM PRZYJECIE_ZEWNETRZE_POZYCJE"), conn)
    aktywne_dos = pd.read_sql(text("SELECT * FROM AKTYWNE_DOSTAWY"), conn)
    zam_pianki_db = pd.read_sql(text("select * from ZAM_PIANKI"), conn)
    zamowienia_niedostarczone = pd.read_sql(text("select LP, TYDZIEN, KOD, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY, ZAM1, ZAM2, POTW_DATA_DOS_1, POTW_DATA_DOS_2, nr_SAMOCHODU from ZAM_PIANKI where STATUS_KOMPLETACJA is null"), conn)
    zns = pd.read_sql(text("select LP, KOD, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY, POTW_DATA_DOS_1, POTW_DATA_DOS_2, DATA_DOSTARCZENIA_1, DATA_DOSTARCZENIA_2, nr_PZ, nr_PW, STATUS_KOMPLETACJA from ZAM_PIANKI where STATUS_KOMPLETACJA is not null and STATUS_KOMPLETACJA <> '1'"), conn)

zns["dostarczone"] = zns.apply(lambda x: x.ZNACZNIK_DOSTAWCY.__len__() == x.STATUS_KOMPLETACJA.__len__(), axis=1)
zamowienia_niespakowane = zns[zns.dostarczone][zns.columns[:-1]]

zpd = zam_pianki_db[["LP", "KOD", "TYDZIEN", "NR_KOMPLETACJI", "OPIS", "ILE_ZAMOWIONE", "ZNACZNIK_DOSTAWCY", "STATUS_KOMPLETACJA"]]


def przesuniecie_daty_dostawy(model, nr_kompletacji):
    return zam_pianki_db[(zam_pianki_db.MODEL == model)&(zam_pianki_db.NR_KOMPLETACJI == nr_kompletacji)&(zam_pianki_db.nr_PZ.isna())][["LP","OPIS","ILE_ZAMOWIONE","POTW_DATA_DOS_1","POTW_DATA_DOS_2","ZNACZNIK_DOSTAWCY","STATUS_KOMPLETACJA", "nr_SAMOCHODU"]]


#PZ
def przyjecie_dostawy(model, nr_kompl, lista_dostarczonych_bryl=None, szybkie_uzupelnienie=None):
  lbp = zam_pianki_db[(zam_pianki_db.MODEL == model)&(zam_pianki_db.NR_KOMPLETACJI == nr_kompl)][["LP", "MODEL", "NR_KOMPLETACJI", "OPIS", "ILE_ZAMOWIONE", "ZNACZNIK_DOSTAWCY", "ZAM1", "ZAM2", "DATA_DOSTARCZENIA_1", "DATA_DOSTARCZENIA_2", "nr_SAMOCHODU", "STATUS_KOMPLETACJA", "nr_PZ",  ]]

  if lista_dostarczonych_bryl == None:
    return lbp
  elif lista_dostarczonych_bryl == True:
    return {i[1].OPIS: {"LP": i[1].LP, "SK": i[1].STATUS_KOMPLETACJA, "DATA_DOS1": i[1].DATA_DOSTARCZENIA_1, "DATA_DOS2": i[1].DATA_DOSTARCZENIA_2, "nr_PZ": i[1].nr_PZ} for i in lbp.iterrows()}
  elif type(lista_dostarczonych_bryl) == dict:
    for k in lista_dostarczonych_bryl.values():
      stmt_update = (update(ZAM_PIANKI)
        .where((ZAM_PIANKI.lp == k["LP"]))
        .values(data_dos1 = k["DATA_DOS1"],
                data_dos2 = k["DATA_DOS2"],
                status_kompletacja = k["SK"],
                nr_pz = k["nr_PZ"]))

      session.execute(stmt_update)
      session.commit()

#ZAKOŃCZ POZYCJE W ZAM_PIANKI
def Zakocz_pozycje_w_ZAM_PIANKI(nrpw):
    """
    nrpw -> nr przyjmowanego pw
    """


    with engine.begin() as conn:
        pw = pd.read_sql(text(f"SELECT * FROM PRZYJECIE_WEWNETRZNE WHERE PW = '{nrpw}'"), conn)

    pw_zpd = pw.merge(zpd[~zpd.STATUS_KOMPLETACJA.isin(["1",None])][["TYDZIEN", "NR_KOMPLETACJI", "KOD", "LP", "ILE_ZAMOWIONE", "ZNACZNIK_DOSTAWCY", "STATUS_KOMPLETACJA"]], left_on=["KOD", "KOMPLETACJA"], right_on=["KOD", "NR_KOMPLETACJI"], how="left")
    # pw_zpd


    stmt = (update(ZAM_PIANKI)
            .where(ZAM_PIANKI.lp.in_(pw_zpd.dropna().LP.astype(int).values.tolist()))
            .values(status_kompletacja = "ZAKONCZONO," , nr_pw=nrpw))


    session.execute(stmt)
    session.commit()

    
