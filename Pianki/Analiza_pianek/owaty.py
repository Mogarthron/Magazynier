import pandas as pd
import json
from Modele_db.modele_db import * 

# with open("./linki.json") as f:
#   linki = json.load(f)
#   path_dane_pianki = linki["path_dane_pianki"]
  # owaty_linki = linki["owaty"]
#   zam_pianki_link = linki["zam_pianki_link"]

#@title OWATY
# _owaty = pd.read_excel(owaty_linki, sheet_name="Arkusz1")
with engine.begin() as conn:
  _owaty = pd.read_sql(text("SELECT * FROM OWATY"), conn)

#w zamowieniu podajemy ilosc belek, na FV dostajemy całkwitą ilosc metrów kwadratowych dla danego typu

ozn_owat = {                  #g/m2, szer, mb
    "O1": ["B/16/150 (1.6x50)", 150, 1.6, 50, "zielona", "73.115.00001"],
    "O2": ["B/16/200 (1.2x40)", 200, 1.2, 40, "niebieska", "73.120.00001"],
    "O3": ["B/16/200 (1.6x40)", 200, 1.6, 40, "czerwona", "73.120.00002"],
}
# wyjatki
# ama 3,5 uważać!!
# hud NW
# wil uważać!!!
# hor 3
# hor 3,5
# sto z50
# sto z70
# sto 3,5
# max z70
# max z60
# oxy 5

def wyczysc_zuzcie(x):
  if type(x) == float:
    return x
  elif type(x) == int:
    return float(x)

  x = x.rstrip()
  if x[-1] == ".":
    x = x[:-1]

  try:
    return float(x)
  except:
    return 99999.0

# _owaty["ZUZYCIE"] = _owaty.ZUZYCIE_mb.apply(wyczysc_zuzcie)
# _owaty["TYP_OWATY"] = _owaty.NAZWA_UKL.apply(lambda x: x[:2].replace("0", "O"))
_owaty["RODZINA_NAZWA"] = _owaty.OPIS.fillna("BRAK").apply(lambda x: x[:3])

typy_owat = _owaty.TYP_OWATY.unique()


ltypy = list()
for t in typy_owat:
  df = _owaty[(_owaty.TYP_OWATY == t)&(_owaty.RODZINA_NAZWA != "BRA")]
  df.rename(columns={"ZUZYCIE": t}, inplace=True)
  ltypy.append(df[["OPIS", t]])

owaty = ltypy[0]
for t in ltypy[1:]:
  owaty = owaty.merge(t, how="outer", on="OPIS").fillna(0)