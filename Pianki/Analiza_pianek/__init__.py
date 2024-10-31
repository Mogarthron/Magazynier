import json
from datetime import datetime as dt, timedelta

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

# with open("./linki.json") as f:
#   linki = json.load(f)
#   path_dane_pianki = linki["path_dane_pianki"]

with open("daty_kompletacji.json") as f:
    dkom = json.load(f)
    daty_kompletacji = dkom["daty_kompletacji"]
    plik_DANE_PIANKI = dkom["plik_dane_pianki"]

# for k in daty_kompletacji:
#     daty_kompletacji[k] = dt.strptime(daty_kompletacji[k], "%Y-%m-%d")

# data_WST = daty_kompletacji[list(daty_kompletacji.keys())[-1]] + timedelta(7)


# pda = list(daty_kompletacji.keys())

from ..Analiza_pianek.przygotowanie_danych import *

class Tabela_analizy():

  def __init__(self, pda) -> None:
    
    saldo = pd.DataFrame(session.query(SALDO.kod, SALDO.stan).all(), 
                         columns=["KOD", "SALDO"])
    
    naliczone = pd.DataFrame(session.query(NALICZONE.limit_nazwa, 
                                           NALICZONE.kod, 
                                           NALICZONE.zapot_zlec, 
                                           NALICZONE.limit_data_prod), 
                                           columns=["LIMIT_NAZWA", "KOD", "ZAPOT_ZLEC", "LIMIT_DATA_PROD"])
    
    wstrzymane = pd.DataFrame(session.query(WSTRZYMANE.kod, WSTRZYMANE.ilosc), 
                              columns=["KOD", "ILOSC"]).drop_duplicates("KOD")#.query("KOD.str.contains('16.')", engine='python')


    #PACZKI Z ZAMÓWIENIAMI
    nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD").ZAPOT_ZLEC.sum().reset_index().rename(columns={"ZAPOT_ZLEC": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]


    with engine.begin() as conn:
      komplety_pianek = pd.read_sql(text("""SELECT KOD, OPIS, CZY_BRYLA, BRYLA_GEN, MAX, obj 
                                            FROM KOMPLETY_PIANEK 
                                            WHERE MAX > 0"""), conn)

    komplety_pianek['CZY_BRYLA'] = komplety_pianek['CZY_BRYLA'].fillna(1)
    komplety_pianek['BRYLA_GEN'] = komplety_pianek['BRYLA_GEN'].fillna("").astype(str).apply(lambda x: x.replace(".", ","))
    komplety_pianek["RODZINA_NAZWA"] = komplety_pianek.OPIS.apply(lambda x: x[:3])

    _analiza = komplety_pianek.merge(
      right=saldo[["KOD","SALDO"]], how="left", on="KOD").merge(
      right=naliczone.groupby("KOD").ZAPOT_ZLEC.sum().reset_index(), how="left", on="KOD").merge(
      right=wstrzymane, how="left", on="KOD").merge(
      right=zam_nie_spakowane.groupby("KOD").sum()["CZEKA_NA_SPAKOWANIE"].reset_index(), how="left", on="KOD").merge(
      right=pianki_w_drodze.groupby("KOD").sum()["ZAMOWIONE"].reset_index(), how="left", on="KOD").merge(
      right=pianki_czesciowo_dostarczone.groupby("KOD").sum()["CZESIOWO_DOSTARCZONE"].reset_index(), how="left", on="KOD")



    for nal_paczka in nal_paczki:
      _analiza = _analiza.merge(nal_paczka, how="left", on="KOD")

    _analiza.rename(columns={"ILOSC": "WST", "ZAPOT_ZLEC":"ZLECENIA", "ILE_ZAMOWIONE": "ZAM"}, inplace=True)

    def do_zam_szt(max_,wolne,zam,czek_na_spak, czesiowo_dos):
      """sztuki do zamowienia"""
      s = max_ - wolne - zam - czek_na_spak - czesiowo_dos
      if s > 0:
        return s
      return 0

    _analiza.fillna(0, axis=1, inplace=True)
    _analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]] = _analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]].astype(float)
    _analiza["MIN"] = (_analiza.MAX/2).round(0).astype(int)
    _analiza["SUMA_ZLEC"] = (_analiza.ZLECENIA + _analiza.WST)
    _analiza["SALDO_Z_NIE_SPAK"] = _analiza.SALDO + _analiza.CZEKA_NA_SPAKOWANIE
    _analiza["WOLNE_SALDO"] = (_analiza.SALDO - _analiza.SUMA_ZLEC)
    _analiza["WOLNE_NIE_SPAK"] = (_analiza.SALDO_Z_NIE_SPAK - _analiza.SUMA_ZLEC)
    _analiza["MIN_obj"] = (_analiza.MIN * _analiza.obj)
    _analiza["MAX_obj"] = (_analiza.MAX * _analiza.obj)
    _analiza["ZAMOWIONE_obj"] = (_analiza.ZAMOWIONE * _analiza.obj)
    _analiza["CZEKA_NA_SPAKOWANIE_obj"] = (_analiza.CZEKA_NA_SPAKOWANIE * _analiza.obj)
    _analiza["CZESCIOWO_DOSTARCZONE_obj"] = (_analiza.CZESIOWO_DOSTARCZONE * _analiza.obj)
    _analiza["ZAMOWIONE_NIE_PRZYJETE_obj"] = _analiza.ZAMOWIONE_obj + _analiza.CZEKA_NA_SPAKOWANIE_obj + _analiza.CZESCIOWO_DOSTARCZONE_obj
    _analiza["SALDO_obj"] = (_analiza.SALDO * _analiza.obj)
    _analiza["WOLNE_obj"] = (_analiza.WOLNE_SALDO * _analiza.obj)
    _analiza["WOLNE_NIE_SPAK_obj"] = (_analiza.WOLNE_NIE_SPAK * _analiza.obj)
    _analiza["DO_ZAM_SZT"] = _analiza.apply(lambda x: do_zam_szt(x.MAX, x.WOLNE_SALDO, x.ZAMOWIONE, x.CZEKA_NA_SPAKOWANIE, x.CZESIOWO_DOSTARCZONE), axis=1)
    _analiza["DO_ZAM_obj"] = (_analiza.DO_ZAM_SZT * _analiza.obj)

    self._analiza = _analiza
    self.analiza = _analiza













##################################################
#STARA LOGIKA 
##################################################
analiza = komplety_pianek.merge(
    right=saldo[["KOD","SALDO"]], how="left", on="KOD").merge(
    # right=naliczone.groupby("KOD_ART").sum().reset_index(), how="left", left_on="KOD", right_on="KOD_ART").merge(
    right=naliczone.groupby("KOD").ZAPOT_ZLEC.sum().reset_index(), how="left", on="KOD").merge(
    right=wstrzymane, how="left", on="KOD").merge(
    right=zam_nie_spakowane.groupby("KOD").sum()["CZEKA_NA_SPAKOWANIE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_w_drodze.groupby("KOD").sum()["ZAMOWIONE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_czesciowo_dostarczone.groupby("KOD").sum()["CZESIOWO_DOSTARCZONE"].reset_index(), how="left", on="KOD")

for nal_paczka in nal_paczki:
  analiza = analiza.merge(nal_paczka, how="left", on="KOD")

analiza.rename(columns={"ILOSC": "WST", "ZAPOT_ZLEC":"ZLECENIA", "ILE_ZAMOWIONE": "ZAM"}, inplace=True)

def do_zam_szt(max_,wolne,zam,czek_na_spak, czesiowo_dos):
  """sztuki do zamowienia"""
  s = max_ - wolne - zam - czek_na_spak - czesiowo_dos
  if s > 0:
    return s
  return 0

# analiza.drop("KOD_ART", axis=1, inplace=True)
analiza.fillna(0, axis=1, inplace=True)
analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]] = analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]].astype(float)
analiza["MIN"] = (analiza.MAX/2).round(0).astype(int)
analiza["SUMA_ZLEC"] = (analiza.ZLECENIA + analiza.WST)
analiza["SALDO_Z_NIE_SPAK"] = analiza.SALDO + analiza.CZEKA_NA_SPAKOWANIE
analiza["WOLNE_SALDO"] = (analiza.SALDO - analiza.SUMA_ZLEC)
analiza["WOLNE_NIE_SPAK"] = (analiza.SALDO_Z_NIE_SPAK - analiza.SUMA_ZLEC)
analiza["MIN_obj"] = (analiza.MIN * analiza.obj)
analiza["MAX_obj"] = (analiza.MAX * analiza.obj)
analiza["ZAMOWIONE_obj"] = (analiza.ZAMOWIONE * analiza.obj)
analiza["CZEKA_NA_SPAKOWANIE_obj"] = (analiza.CZEKA_NA_SPAKOWANIE * analiza.obj)
analiza["CZESCIOWO_DOSTARCZONE_obj"] = (analiza.CZESIOWO_DOSTARCZONE * analiza.obj)
analiza["ZAMOWIONE_NIE_PRZYJETE_obj"] = analiza.ZAMOWIONE_obj + analiza.CZEKA_NA_SPAKOWANIE_obj + analiza.CZESCIOWO_DOSTARCZONE_obj
analiza["SALDO_obj"] = (analiza.SALDO * analiza.obj)
analiza["WOLNE_obj"] = (analiza.WOLNE_SALDO * analiza.obj)
analiza["WOLNE_NIE_SPAK_obj"] = (analiza.WOLNE_NIE_SPAK * analiza.obj)
analiza["DO_ZAM_SZT"] = analiza.apply(lambda x: do_zam_szt(x.MAX, x.WOLNE_SALDO, x.ZAMOWIONE, x.CZEKA_NA_SPAKOWANIE, x.CZESIOWO_DOSTARCZONE), axis=1)
analiza["DO_ZAM_obj"] = (analiza.DO_ZAM_SZT * analiza.obj)


def Zapis_danych_do_Archiwum(nr_tygodnia, analiza, _Tabela_podsumowania_analizy, url_do_bazy):
  from Modele_db import create_engine 
  zapis_analizy_engine = create_engine(url_do_bazy, echo=False)


  zapis_analizy =analiza[["KOD","MAX","SALDO","SUMA_ZLEC","ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE",]]
  zapis_analizy["TYDZIEN"] = nr_tygodnia
  zapis_analizy[["MAX","SALDO","SUMA_ZLEC","ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE"]] = zapis_analizy[["MAX","SALDO","SUMA_ZLEC","ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE"]].astype("int16")

  zapis_analizy.to_sql("ZAPIS_ANALIZY_PIANKI", zapis_analizy_engine, index=False, if_exists="append")

  tpa = _Tabela_podsumowania_analizy
  tpa["TYDZIEN"] = nr_tygodnia
  tpa.to_sql("TABELA_PODSUMOWANIA_ANALIZY", zapis_analizy_engine, index=False, if_exists="append")
