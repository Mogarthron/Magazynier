import pandas as pd
from Modele_pianek import engine, text

from datetime import datetime as dt, timedelta
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')

import json
with open("./linki.json") as f:
  linki = json.load(f)
  zam_pianki_link = linki["zam_pianki_link"]


with engine.begin() as conn:
      tab = pd.read_sql(text("SELECT * from baza_PIANKI"), conn)
      zp_tab = pd.read_sql(text("SELECT * from ZAM_PIANKI"), conn)# WHERE STATUS_KOMPLETACJA <> '1'
zp_tab["KOMPLETACJA"] = zp_tab["MODEL"] + " " + zp_tab["NR_KOMPLETACJI"]
zp_tab["nr_SAMOCHODU"].fillna("", inplace=True)
zp_tab = zp_tab[zp_tab.STATUS_KOMPLETACJA !="1"]

tab["vol"] = tab.DLUG*tab.SZER*tab.WYS/1000_000_000
tab["VOL"] = tab.vol*tab.ilosc


def obietosci_samochodow(dostawca, tabela):

  dostawy = tabela[tabela.nr_SAMOCHODU.str.contains(dostawca)]

  dostawy["SAMOCHOD"] = dostawy.nr_SAMOCHODU.apply(lambda x: [d for d in x.split(",") if dostawca in d][0])

  dostawy = dostawy.merge(komplety_pianek[["KOD", "BRYLA_GEN"]], how="left", on="KOD")

  def obj_typ(m,bg,g,s,l,i,t):
    war_len = (tab.TYP == "G-401")
    war_shr = (tab.TYP.str.contains("HR|EE"))

    if t == "g":
      return tab[(tab.MODEL == m) & (tab.BRYLA == bg) & ~war_len & ~war_shr].VOL.sum()*i if g == dostawca[0] else 0
    if t == "s":
      return tab[(tab.MODEL == m) & (tab.BRYLA == bg) & (war_shr)].VOL.sum()*i if s == dostawca[0] else 0
    if t == "l":
      return tab[(tab.MODEL == m) & (tab.BRYLA == bg) & (war_len)].VOL.sum()*i if l == dostawca[0] else 0

    # return f"{gal} + {shr} + {len}"
    # return gal + shr + len

  dostawy["GAL_OBJ"] = dostawy.apply(lambda x: obj_typ(x.MODEL, x.BRYLA_GEN, x.GALANTERIA, x.SIEDZISKA_HR, x.LENIWA, x.ILE_ZAMOWIONE, "g"), axis=1)
  dostawy["SHR_OBJ"] = dostawy.apply(lambda x: obj_typ(x.MODEL, x.BRYLA_GEN, x.GALANTERIA, x.SIEDZISKA_HR, x.LENIWA, x.ILE_ZAMOWIONE, "s"), axis=1)
  dostawy["LEN_OBJ"] = dostawy.apply(lambda x: obj_typ(x.MODEL, x.BRYLA_GEN, x.GALANTERIA, x.SIEDZISKA_HR, x.LENIWA, x.ILE_ZAMOWIONE, "l"), axis=1)
  dostawy["OBJ"] = dostawy.GAL_OBJ + dostawy.SHR_OBJ + dostawy.LEN_OBJ

  return dostawy[["KOMPLETACJA", "OPIS", 'ILE_ZAMOWIONE', 'SAMOCHOD', "GAL_OBJ", "SHR_OBJ", "LEN_OBJ", "OBJ"]]
  # return dostawy.groupby("SAMOCHOD").sum().OBJ, dostawy.groupby(["SAMOCHOD", "KOMPLETACJA"]).sum().OBJ