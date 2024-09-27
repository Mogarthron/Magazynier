import json
from datetime import datetime as dt, timedelta

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

with open("./linki.json") as f:
  linki = json.load(f)
  path_dane_pianki = linki["path_dane_pianki"]

with open("daty_kompletacji.json") as f:
    dkom = json.load(f)
    daty_kompletacji = dkom["daty_kompletacji"]
    plik_DANE_PIANKI = dkom["plik_dane_pianki"]

for k in daty_kompletacji:
    daty_kompletacji[k] = dt.strptime(daty_kompletacji[k], "%Y-%m-%d")

data_WST = daty_kompletacji[list(daty_kompletacji.keys())[-1]] + timedelta(7)


pda = list(daty_kompletacji.keys())

from ..Analiza_pianek.przygotowanie_danych import *


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
analiza["MAX_obj"] = (analiza.MAX * analiza.obj)
analiza["ZAMOWIONE_obj"] = (analiza.ZAMOWIONE * analiza.obj)
analiza["CZEKA_NA_SPAKOWANIE_obj"] = (analiza.CZEKA_NA_SPAKOWANIE * analiza.obj)
analiza["CZESCIOWO_DOSTARCZONE_obj"] = (analiza.CZESIOWO_DOSTARCZONE * analiza.obj)
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
