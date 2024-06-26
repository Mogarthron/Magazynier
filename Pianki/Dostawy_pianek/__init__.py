import pandas as pd
from Modele_db import engine, text
from ..Analiza_pianek import komplety_pianek

from datetime import datetime as dt, timedelta
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')

# import json
# with open("./linki.json") as f:
#   linki = json.load(f)
#   zam_pianki_link = linki["zam_pianki_link"]


with engine.begin() as conn:
      tab = pd.read_sql(text("SELECT * from baza_PIANKI"), conn)
      zp_tab = pd.read_sql(text("""SELECT LP, TYDZIEN, KOD, MODEL, NR_KOMPLETACJI, OPIS,
                                          ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY, GALANTERIA, SIEDZISKA_HR,
                                          LENIWA, ZAM1, ZAM2, UWAGI, POTW_DATA_DOS_1, POTW_DATA_DOS_2,
                                          nr_SAMOCHODU, nr_PARTII 
                                  FROM ZAM_PIANKI --WHERE STATUS_KOMPLETACJA NOT LIKE '%ZAKO%' AND NR_PARTII IS NOT NULL"""), conn)
zp_tab["KOMPLETACJA"] = zp_tab["MODEL"] + " " + zp_tab["NR_KOMPLETACJI"]
zp_tab["nr_SAMOCHODU"].fillna("", inplace=True)

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


def wykers_zapelnienia_samochodow(tabela_obietosci_samochodow):
  fig = px.bar(tabela_obietosci_samochodow, x="OBJ", y="SAMOCHOD", color='KOMPLETACJA', orientation='h',
              text="KOMPLETACJA",
              hover_data=["KOMPLETACJA", "GAL_OBJ","SHR_OBJ","LEN_OBJ"],
              #  height=400,
              title=f'Zapełnienie samochodów {dt.now().strftime("%Y-%m-%d")}')
  fig.update_yaxes(autorange="reversed")
  fig.update_layout(showlegend=False)
  fig.add_vline(x=30, line_dash="dash", annotation_text="30m3")
  fig.add_vline(x=60, line_dash="dash", annotation_text="60m3")
  fig.add_vline(x=90, line_dash="dash", annotation_text="90m3")
  fig.add_vline(x=100, line_color="red")

  return fig
# fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
# fig.show()