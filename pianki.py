import pandas as pd
import numpy as np

from sqlalchemy import create_engine, text
engine = create_engine("sqlite:///GENERATORY.db", echo=False)
lista_bryl = dict()
with engine.begin() as conn:
      lb = conn.execute(text(f"SELECT * from lista_bryl_pianki"))
      tab = pd.read_sql(text("SELECT * from baza_PIANKI"), conn)
for i in lb:
  # print(i[0], i[1].split("_"))
  lista_bryl[i[0]] = [x for x in i[1].split("_")]

# print(lista_bryl["REVERSO"])

# @title FUNKCJE
# def bryla_pianki(MODEL, BRYLA, ile_zam):
#   df = tab[(tab.MODEL == MODEL) &(tab.BRYLA == BRYLA)]
#   df.ilosc = df.ilosc * ile_zam
#   df.ilosc = df.ilosc.astype(np.int32)

#   return df

# def zestawienie_pianek_modelu(model, bryly):
#   lt = list()
#   lista_opisowa = list()

#   for i in bryly:
#     lt.append(bryla_pianki(model, i, bryly[i]))

#   pianki = pd.concat(lt).groupby("NUMER").sum().reset_index()[["NUMER", "ilosc"]]

#   def vol(N, i):
#     _vol = tab[tab.NUMER == N][["WYS", "SZER", "DLUG"]].drop_duplicates()
#     return i * _vol["WYS"].values[0] * _vol["SZER"].values[0] * _vol["DLUG"].values[0] / 1000_000_000

#   pianki["VOL"] = pianki.apply(lambda x: vol(x.NUMER, x.ilosc), axis=1)


#   for n in pianki.NUMER.index:
#     t = tab[(tab.MODEL == m) & (tab.NUMER == pianki.NUMER.iloc[n])]
#     num = pianki.NUMER.iloc[n]
#     typ = t.TYP.unique()[0]
#     profil = t.PROFIL.unique()[0]
#     ozn = t.OZN.unique()[0]
#     opis = t.PRZEZ.unique()[0]
#     wymiar = t.WYMIAR.unique()[0]
#     bryly = [x for x in t.BRYLA.tolist() if x in list(b.keys())]

#     lista_opisowa.append([num,typ,profil,ozn,opis,wymiar,bryly])

#   maks = 1
#   for i in lista_opisowa:
#     if len(i[-1]) > maks:
#       maks = len(i[-1])
#     # print(len(i[-1]), maks)

#   for i in lista_opisowa:
#     if len(i[-1]) < maks:
#       for _ in range(maks - len(i[-1])):
#         i[-1].append(" ")
#     # print(i[-1])
#   lo_b = [x[-1] for x in lista_opisowa]

#   zpm = pianki.merge(pd.concat([pd.DataFrame([x[:-1] for x in lista_opisowa], columns=["NUMER", "TYP", "PROFIL", "OZN", "OPIS", "WYMIAR"]),
#             pd.DataFrame(lo_b, columns=[f"br{x}" for x in range(1, maks+1)])],axis=1), how="left", on="NUMER")

#   return zpm


# @title KLASY

class Pianki:

  def __init__(self, MODEL:str, galanteria, siedziska_HR, leniwa, PIANPOL=False):

    self.galanteria = galanteria
    self.siedziska_HR = siedziska_HR
    self.leniwa = leniwa

    self.Model = MODEL
    self.vita_VOL = 0
    self.ciech_VOL = 0
    self.pianpol_VOL = 0

    with engine.begin() as conn:
      query = text(f"SELECT * from baza_PIANKI WHERE MODEL = '{MODEL}'")
      self.tab = pd.read_sql(query, conn)


  def __bryla_pianki(self, BRYLA, ile_zam):
    df = self.tab[self.tab.BRYLA == BRYLA]
    df.ilosc = df.ilosc * ile_zam
    df.ilosc = df.ilosc.astype(np.int32)

    return df

  def zestawienie_pianek_modelu(self, bryly:dict):
    lt = list()
    lista_opisowa = list()

    for i in bryly:
      lt.append(self.__bryla_pianki(i, bryly[i]))

    pianki = pd.concat(lt).groupby("NUMER").sum().reset_index()[["NUMER", "ilosc"]]

    def vol(N, i):
      _vol = self.tab[self.tab.NUMER == N][["WYS", "SZER", "DLUG"]].drop_duplicates()
      return i * _vol["WYS"].values[0] * _vol["SZER"].values[0] * _vol["DLUG"].values[0] / 1000_000_000

    pianki["VOL"] = pianki.apply(lambda x: vol(x.NUMER, x.ilosc), axis=1)

    for n in pianki.NUMER.index:
      t = self.tab[self.tab.NUMER == pianki.NUMER.iloc[n]]
      num = pianki.NUMER.iloc[n]
      typ = t.TYP.unique()[0]
      profil = t.PROFIL.unique()[0]
      ozn = t.OZN.unique()[0]
      opis = t.PRZEZ.unique()[0]
      wymiar = t.WYMIAR.unique()[0]
      #{self.Model[:3]} opis modelu do br poniżej
      br = [f"{self.Model[:3]} {x} {t[t.BRYLA == x].ilosc.values[0]*bryly[x]:.0f}szt" for x in t.BRYLA.tolist() if x in list(bryly.keys())]

      lista_opisowa.append([num,typ,profil,ozn,opis,wymiar,br])

    maks = 1
    for i in lista_opisowa:
      if len(i[-1]) > maks:
        maks = len(i[-1])
      # print(len(i[-1]), maks)

    for i in lista_opisowa:
      if len(i[-1]) < maks:
        for _ in range(maks - len(i[-1])):
          i[-1].append(" ")
      # print(i[-1])
    lo_b = [x[-1] for x in lista_opisowa]

    zpm = pianki.merge(pd.concat([pd.DataFrame([x[:-1] for x in lista_opisowa], columns=["NUMER", "TYP", "PROFIL", "OZN", "OPIS", "WYMIAR"]),
              pd.DataFrame(lo_b, columns=[f"br{x}" for x in range(1, maks+1)])],axis=1), how="left", on="NUMER")

    return zpm

  def __add__(self, other):
      if type(other) == dict:
        return {"VITA": self.vita_VOL + other["VITA"],
                "CIECH": self.ciech_VOL + other["CIECH"],
                "PIANPOL": self.pianpol_VOL + other["PIANPOL"]}

      else:
        return {"VITA": self.vita_VOL + other.vita_VOL,
                "CIECH": self.ciech_VOL + other.ciech_VOL,
                "PIANPOL": self.pianpol_VOL + other.pianpol_VOL}

  def __radd__(self, other):
    return self.__add__(other)



class CIECH(Pianki):

  mod_VOL_ciech = 1
  MODEL = ""
  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL)

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}
    self.ciech = self.zestawienie_pianek_modelu(b)


    self.vita_VOL = 0
    self.ciech_VOL = self.ciech.VOL.sum()*self.mod_VOL_ciech

  def __repr__(self):
    return f"{self.MODEL} Vol Ciech: {self.ciech_VOL:.2f}m3"


# print(tab[(tab.MODEL == "AMALFI")&(tab.TYP == "G-401")&(tab.BRYLA.isin(["[RS", "RS]", "NW", "WN", "[LA", "LA]"]))])

# @title KLASY PIANEK M1
class MODEL1(Pianki):
  """
  MODEL1 rozdziału pianek na siediska HR-3020 vita reszta ciech
  bm -> bryły z analizy
  bg -> bryły z generatora
  """
  mod_VOL_ciech = 1
  mod_VOL_vita = 1
  MODEL = ""

  def __init__(self, b=None):
    super().__init__(MODEL=self.MODEL, galanteria="C", siedziska_HR="V", leniwa="C")



    if type(b) == dict:
      self.bryly = {k:v for k,v in b.items()}# if b[k] != 0}
      self.BRYLY_ZAM = "BRAK BRYŁ Z ANALIZY"

    elif type(b) == pd.DataFrame:
      print("DOROBIC LOGIKE!!")

    self.zpm = self.zestawienie_pianek_modelu(b)

    filtr_vita = (self.zpm.TYP == "HR-3020") & (self.zpm.OPIS == "siedzisko")

    self.vita = self.zpm[filtr_vita]
    self.ciech = self.zpm[~filtr_vita]
    self.vita_VOL = self.vita.VOL.sum()*self.mod_VOL_vita
    self.ciech_VOL = self.ciech.VOL.sum()*self.mod_VOL_ciech
    self.siedziska_VOL = self.vita[self.vita.TYP == "HR-3020"].VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Vita: {self.vita_VOL:.2f}m3, Vol Ciech: {self.ciech_VOL:.2f}m3"


class AMALFI(MODEL1):

  mod_VOL_ciech = 0.9
  MODEL = "AMALFI"

  def __init__(self, b:dict, b_memory={"NW":0}):
    super().__init__(b=b)

    ama_mem_pianki = tab[(tab.MODEL == "AMALFI")&(tab.TYP == "G-401")&(tab.BRYLA.isin(["[RS", "RS]", "NW", "WN", "[LA", "LA]"]))]

class ELIXIR(MODEL1):
  MODEL = "ELIXIR"
  def __init__(self,b:dict):
    super().__init__(b=b)

class REVERSO(MODEL1):
  MODEL = "REVERSO"
  def __init__(self,b=None):
    super().__init__(b=b)

class WILLOW(MODEL1):
  mod_VOL_ciech = 0.95
  MODEL = "WILLOW"
  def __init__(self, b:dict):
    super().__init__(b=b)

class OXYGEN(MODEL1):
  mod_VOL_ciech = 0.95
  MODEL = "OXYGEN"
  def __init__(self, b:dict):
    super().__init__(b=b)


# @title KLASY PIANEK M2

class MODEL2(Pianki):
  """
  MODEL2 rozdziału pianek na Memory Ciech reszta Vita
  bm -> btyły z analizy
  bg -> bryły z generatora
  """

  mod_VOL_ciech = 1
  mod_VOL_vita = 1
  MODEL = ""
  converter=dict()
  def __init__(self, bg:dict):
    super().__init__(MODEL=self.MODEL, galanteria="V", siedziska_HR="V", leniwa="C")



    if bg != None:
      b = bg
      self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)

    filtr_vita = (self.zpm.TYP != "G-401")

    self.vita = self.zpm[filtr_vita]
    self.ciech = self.zpm[~filtr_vita]
    self.vita_VOL = self.vita.VOL.sum()*self.mod_VOL_vita
    self.ciech_VOL = self.ciech.VOL.sum()*self.mod_VOL_ciech
    self.siedziska_VOL = self.vita[self.vita.TYP == "HR-3020"].VOL.sum()


  def __repr__(self):
    return f"{self.MODEL} Vol Vita: {self.vita_VOL:.2f}m3, Vol Ciech: {self.ciech_VOL:.2f}m3"



class HORIZON(MODEL2):
  MODEL = "HORIZON"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class LOBBY(MODEL2):
  MODEL = "LOBBY"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class DUO(MODEL2):
  MODEL = "DUO"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class MAXWELL(MODEL2):
  MODEL = "MAXWELL"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class ONYX(MODEL2):
  MODEL = "ONYX"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class COCO(MODEL2):
  MODEL = "COCO"
  def __init__(self,b:dict):
    super().__init__(bg=b)


# @title KLASY PIANEK M3
#Model rozdziału paneka Memory olta reszta VITA

class MODEL3(Pianki):
  """
  Model3 rozdziału paneka Memory olta reszta VITA
  olta -> zwaraca liste pianek memory do wycięcia w olcie
  """
  mod_VOL_ciech = 1
  mod_VOL_vita = 1
  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="V", siedziska_HR="V", leniwa="O")



    self.bryly = b
    self.zpm = self.zestawienie_pianek_modelu(b)

    filtr_model3 = (self.zpm.TYP != "G-401")

    self.vita = self.zpm[filtr_model3]
    self.olta = self.zpm[~filtr_model3]
    self.vita_VOL = self.vita.VOL.sum()*self.mod_VOL_vita
    self.ciech_VOL = 0
    self.siedziska_VOL = self.vita[self.vita.TYP == "HR-3020"].VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Vita: {self.vita_VOL:.2f}m3"



class STONE(MODEL3):
  MODEL = "STONE"
  def __init__(self,b:dict):
    super().__init__(b=b)

class UNO(MODEL3):
  MODEL = "UNO"
  def __init__(self,b:dict):
    super().__init__(b=b)


# @title KLASY PIANEK M4

class MODEL4(Pianki):
  """
  MODEL4 komplety brył zamawiane w CIECHU
  bm -> btyły z analizy
  bg -> bryły z generatora
  """

  mod_VOL_ciech = 1
  mod_VOL_vita = 1
  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="C", siedziska_HR="C", leniwa="C")

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)

    # filtr_vita = (self.zpm.TYP != "G-401")

    self.vita = None
    self.ciech = self.zpm
    self.vita_VOL = 0
    self.ciech_VOL = self.ciech.VOL.sum()*self.mod_VOL_ciech


  def __repr__(self):
    return f"{self.MODEL} Vol Ciech: {self.ciech_VOL:.2f}m3"



class CALYPSO(MODEL4):
  MODEL = "CALYPSO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class DIVA(MODEL4):
  MODEL = "DIVA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class HUDSON(MODEL4):
  MODEL = "HUDSON"
  def __init__(self,b:dict):
    super().__init__(b=b)

class RITZ(MODEL4):
  MODEL = "RITZ"
  def __init__(self,b:dict):
    super().__init__(b=b)

class SAMOA(MODEL4):
  MODEL = "SAMOA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class SPECTRA(MODEL4):
  MODEL = "SPECTRA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class GREY(MODEL4):
  MODEL = "GREY"
  def __init__(self,b:dict):
    super().__init__(b=b)

class LENOX(MODEL4):
  MODEL = "LENOX"
  def __init__(self,b:dict):
    super().__init__(b=b)


# @title KLASY PIANEK M5

class MODEL5(Pianki):
  """
  MODEL5 komplety brył zamawiane w PIANPOLU BEZ LENIWEJ
  bm -> btyły z analizy
  bg -> bryły z generatora
  """


  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="P", siedziska_HR="P", leniwa="O")

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)

    filtr_pianpol = (self.zpm.TYP != "G-401")

    self.vita = None
    self.ciech = self.zpm[~filtr_pianpol]
    self.pianpol = self.zpm[filtr_pianpol]
    self.vita_VOL = 0
    self.ciech_VOL = 0
    self.olta_VOL = self.ciech.VOL.sum()
    self.pianpol_VOL = self.pianpol.VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Pianpol: {self.pianpol_VOL:.2f}m3, {self.MODEL} Vol CIECH: {self.ciech_VOL:.2f}m3"


class AVANT_P(MODEL5):
  MODEL = "AVANT"
  def __init__(self,b:dict):
    super().__init__(b=b)

class OVAL_P(MODEL5):
  MODEL = "OVAL"
  def __init__(self,b:dict):
    super().__init__(b=b)

# @title KLASY PIANEK M6

class MODEL6(Pianki):
  """
  MODEL6 komplety brył zamawiane w PIANPOLU
  """


  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="P", siedziska_HR="P", leniwa="P")

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)

    self.vita = None
    self.ciech = None
    self.pianpol = self.zpm
    self.vita_VOL = 0
    self.ciech_VOL = 0
    self.pianpol_VOL = self.pianpol.VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Pianpol: {self.pianpol_VOL:.2f}m3"


class OXYGEN_P(MODEL6):
  MODEL = "OXYGEN"
  def __init__(self,b:dict):
    super().__init__(b=b)

class MAXWELL_P(MODEL6):
  MODEL = "MAXWELL"
  def __init__(self,b:dict):
    super().__init__(b=b)


#ANALIZA PIANEK
from datetime import datetime as dt, timedelta

path_dane_pianki = "dane_excel/DANE_PIANKI_2405.xlsx"
#daty kompletacji
daty_kompletacji = {
                    "02/01":dt(2024,2,7),
                    "03/01":dt(2024,2,14),
                    "04/01":dt(2024,2,21),
                    "04/03":dt(2024,2,14),
                    "05/03":dt(2024,2,21),
                    "05/05":dt(2024,2,21),
                    "05/01":dt(2024,2,28),
                    }

# data_WST = dt.strptime(daty_kompletacji[list(daty_kompletacji.keys())[-1]], "%Y-%m-%d") + timedelta(7)
data_WST = daty_kompletacji[list(daty_kompletacji.keys())[-1]] + timedelta(7)
# print(data_WST)

pda = list(daty_kompletacji.keys())

#OWATY
_owaty = pd.read_excel("dane_excel/111 KROJOWNIA SUROWKI PIANKI OWATY.xlsx", sheet_name="Arkusz1")

#w zamowieniu podajemy ilosc belek, na FV dostajemy całkwitą ilosc metrów kwadratowych dla danego typu

ozn_owat = {                  #g/m2, szer, mb
    "O1": ["B/16/150 (1.6x50)", 150, 1.6, 50, "zielona"],
    "O2": ["B/16/200 (1.2x40)", 200, 1.2, 40, "niebieska"],
    "O3": ["B/16/200 (1.6x40)", 200, 1.6, 40, "czerwona"],
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

_owaty["ZUZYCIE"] = _owaty.ZUZYCIE_mb.apply(wyczysc_zuzcie)
_owaty["TYP_OWATY"] = _owaty.NAZWA_UKL.apply(lambda x: x[:2].replace("0", "O"))
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

#@title PRZYGOTOWANIE DANYCH

#PLIKI ZAM_PIANKI
komplety_pianek = pd.read_excel("dane_excel/ZAM_PIANKI.xlsx", sheet_name="Arkusz3")
komplety_pianek['CZY_BRYLA'] = komplety_pianek['CZY_BRYLA'].fillna(1)
komplety_pianek['BRYLA_GEN'] = komplety_pianek['BRYLA_GEN'].fillna("").astype(str).apply(lambda x: x.replace(".", ","))
komplety_pianek["RODZINA_NAZWA"] = komplety_pianek.OPIS.apply(lambda x: x[:3])


with engine.begin() as conn:
  zam_pianki = pd.read_sql(text("""SELECT TYDZIEN, KOD, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY,
                      ZAM1, ZAM2, POTW_DATA_DOS_1 as dos1, POTW_DATA_DOS_2 as dos2, STATUS_KOMPLETACJA from ZAM_PIANKI WHERE STATUS_KOMPLETACJA IS NOT '1'"""), conn)


def dostarczone(x, y):
    """
    0 - nie dostarczono
    1 - dostarczono częściowo (dodtarczył tylko jeden dostawca)
    2 - czeka na spakowanie
    3 - spakowana częściowo
    """
    if type(y) != str:
      return 0

    if y == np.NaN:
      return 0

    if x == np.NaN:
      return 0

    try:
      if len(x) == len(y):
        return 2
      elif y == "":
        return 0
      else:
        return 1
    except:
      return 9999

# zam_pianki[['ZAM1','ZAM2','spakowana']] = zam_pianki[['ZAM1','ZAM2','spakowana']].fillna("", inplace=True)
zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']] = zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']].fillna("")

zam_pianki["dostarczono"] = zam_pianki.apply(lambda x: dostarczone(x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA), axis=1)


zam_nie_spakowane = zam_pianki[(zam_pianki.dostarczono == 2)]
zam_nie_spakowane.rename(columns={"ILE_ZAMOWIONE": "CZEKA_NA_SPAKOWANIE"}, inplace=True)
pianki_czesciowo_dostarczone = zam_pianki[(zam_pianki.dostarczono == 1)]
pianki_czesciowo_dostarczone.rename(columns={"ILE_ZAMOWIONE": "CZESIOWO_DOSTARCZONE"}, inplace=True)
pianki_w_drodze = zam_pianki[(zam_pianki.STATUS_KOMPLETACJA == "") & (~zam_pianki.ZNACZNIK_DOSTAWCY.isna())]
pianki_w_drodze.rename(columns={"ILE_ZAMOWIONE": "ZAMOWIONE"}, inplace=True)

#PLIK DANE_PIANKI_XXXX
saldo = pd.read_excel(path_dane_pianki, sheet_name="SALDO", usecols="B,D,H")
naliczone = pd.read_excel(path_dane_pianki, sheet_name="NALICZONE", usecols="C,F,Y,Z,AK").query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')", engine='python')
wstrzymane = pd.read_excel(path_dane_pianki, sheet_name="ZLECENIA")#.query("KOD.str.contains('16.')", engine='python')

#PACZKI Z ZAMÓWIENIAMI
nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD_ART").ZAPOTRZ.sum().reset_index().rename(columns={"KOD_ART": "KOD", "ZAPOTRZ": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]

#@title TABELA analiza
analiza = komplety_pianek.merge(
    right=saldo[["KOD","SALDO"]], how="left", on="KOD").merge(
    right=naliczone.groupby("KOD_ART").sum().reset_index(), how="left", left_on="KOD", right_on="KOD_ART").merge(
    right=wstrzymane, how="left", on="KOD").merge(
    right=zam_nie_spakowane.groupby("KOD").sum()["CZEKA_NA_SPAKOWANIE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_w_drodze.groupby("KOD").sum()["ZAMOWIONE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_czesciowo_dostarczone.groupby("KOD").sum()["CZESIOWO_DOSTARCZONE"].reset_index(), how="left", on="KOD")

for nal_paczka in nal_paczki:
  analiza = analiza.merge(nal_paczka, how="left", on="KOD")

analiza.rename(columns={"ILOSC": "WST", "ZAPOTRZ":"ZLECENIA", "ILE_ZAMOWIONE": "ZAM"}, inplace=True)

def do_zam_szt(m,w,zam,czek_na_spak, czesiowo_dos):
  s = m-w-zam - czek_na_spak - czesiowo_dos
  if s > 0:
    return s
  return 0

analiza.drop("KOD_ART", axis=1, inplace=True)
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


def Ogolna_analiza_objetosci(widok = None):
  """
  widok = None -> zestawienie obietosci raportu
  widok = tabelka -> tabelka z wszystkimi objetosciami brył
  widok = podsum -> tabelka z procentowym podsumowaniem wszystkich brył
  widok = podsum_prc -> zestawienie wartosci procentowych raportu
  """
  oao = analiza.groupby("RODZINA_NAZWA")[[x for x in analiza.columns if "obj" in x][1:]].sum()
  oao["SALDO_MAX_prc"] = oao.SALDO_obj / oao.MAX_obj
  oao["WOLNE_MAX_prc"] = oao.WOLNE_obj / oao.MAX_obj
  oao["WOLNE_NIE_SPAK_MAX_prc"] = oao.WOLNE_NIE_SPAK_obj / oao.MAX_obj
  oao["ZAM_I_WOLNE_prc"] = (oao.WOLNE_obj + oao.ZAMOWIONE_obj) / oao.MAX_obj
  oao["DO_ZAM_prc"] = (oao.DO_ZAM_obj / oao.MAX_obj)

  podsum = oao[[x for x in oao if "obj" in x]].sum()
  sm = (podsum.SALDO_obj / podsum.MAX_obj)
  wm = (podsum.WOLNE_obj / podsum.MAX_obj)
  wnsm = (podsum.WOLNE_NIE_SPAK_obj / podsum.MAX_obj)
  wzm = ((podsum.WOLNE_obj + podsum.ZAMOWIONE_obj) / podsum.MAX_obj)

  if widok == "tabelka":
    return oao[[x for x in oao if "obj" in x]]
  elif widok == "podsum":
    return oao[[x for x in oao if "prc" in x]]
  elif widok == "podsum_prc":
    print(f"SALDO / MAX: {sm*100:.1f}%")
    print(f"WOLNE / MAX: {wm*100:.1f}%")
    print(f"WOLNE_NIE_SPAK / MAX: {wnsm*100:.1f}%")
    print(f"ZAPEŁNIENIE MAG PO ZDJECIU {len(pda)} PACZEK RAZEM Z ZAMOWIONYMI: {wzm*100:.1f}%")
  else:
    print(podsum)


def Braki(prt=True, WOLNE="SALDO"):

  kol_2 = pda + ["WST"]

  if WOLNE == "SALDO":
    kol_1 = ["OPIS", "ZAMOWIONE", "SALDO", "WOLNE_SALDO"]
    kol_braki = ["OPIS","WOLNE_SALDO", "SALDO", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_SALDO < 0][kol_1+kol_2]
    saldo = braki.SALDO.to_numpy()

  if WOLNE == "NIE_SPAK":
    kol_1 = ["OPIS", "ZAMOWIONE", "SALDO_Z_NIE_SPAK", "WOLNE_NIE_SPAK"]
    kol_braki = ["OPIS","WOLNE_NIE_SPAK", "SALDO_Z_NIE_SPAK", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_NIE_SPAK < 0][kol_1+kol_2]
    saldo = braki.SALDO_Z_NIE_SPAK.to_numpy()

  kiedy_zabraknie = ["" for x in range(braki.shape[0])]
  sum_zlec = braki[pda[0]].to_numpy()

  saldo_po_paczce = saldo - sum_zlec
  for p in enumerate(saldo_po_paczce):
    if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
      kiedy_zabraknie[p[0]] = pda[0]

  for paczka in pda[1:]:
    saldo_po_paczce -= braki[paczka].to_numpy()
    for p in enumerate(saldo_po_paczce):
      if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
        kiedy_zabraknie[p[0]] = paczka

  saldo_po_paczce -= braki.WST.to_numpy()
  for p in enumerate(saldo_po_paczce):
    if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
      kiedy_zabraknie[p[0]] = "WST"

  braki["PACZKA"] = kiedy_zabraknie

  def data_kompletacji(x):
    if x in list(daty_kompletacji.keys()):

      return daty_kompletacji[x]

    else:
      return data_WST

  braki["DATA_KOMPLETACJI"] = braki.PACZKA.apply(data_kompletacji)#.dt.strftime("%Y-%m-%d")
  braki.set_index(pd.Index([x for x in range(1, braki.shape[0]+1)]),inplace=True)


  return braki[kol_braki], {"POZYCJE": braki.shape[0], "ILOSC_BAKOW": abs(braki[braki.columns[3]].sum())}

def Zagrozone(prt=True, WOLNE="SALDO"):
  if WOLNE == "SALDO":
    zagr = analiza[(analiza.WOLNE_SALDO >= 0) & (analiza.WOLNE_SALDO < analiza.MIN)][["OPIS", "ZAMOWIONE", "SALDO", "MIN", "WOLNE_SALDO"]]
  if WOLNE == "NIE_SPAK":
    zagr = analiza[(analiza.WOLNE_NIE_SPAK >= 0) & (analiza.WOLNE_NIE_SPAK < analiza.MIN)][["OPIS", "ZAMOWIONE", "SALDO_Z_NIE_SPAK", "MIN", "WOLNE_NIE_SPAK"]]


  zagr_nie_zam = zagr[zagr.ZAMOWIONE == 0]

  if prt:
    print(f"PONIZEJ MIN: {zagr.shape[0]} POZYCJE")
    print(f"PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE")
  else:
   return zagr


import plotly.express as px

def Wykres_propozucji_zamowien():
  oao = Ogolna_analiza_objetosci("podsum").reset_index()


  fig = px.bar(oao, x="RODZINA_NAZWA", y="DO_ZAM_prc",
              title="OBIETOŚĆ BRYL DO ZAMOWIENIA DO MAKSYMALNEGO SALDA",
              hover_data=["ZAM_I_WOLNE_prc"])

  fig.add_hline(y=.2)
  fig.show()


#@title KLASA

import plotly.graph_objects as go

class Analiza_Rodziny():
  def __init__(self, cls):

    kol_1 = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_1_MAX = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "MAX", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_2 = pda#"ZLECENIA"
    kol_3 = ["WST", "DO_ZAM_SZT"]
    kol_MAX = kol_1_MAX+kol_2+kol_3
    kol_skr = kol_1
    self.MODEL = cls.MODEL
    self.klasa = cls

    ana = analiza[analiza.RODZINA_NAZWA == cls.MODEL[:3]]
    # ana["ZAMOWIONE_obj"] = (ana.ZAMOWIONE * ana.obj)
    # #'CZEKA_NA_SPAKOWANIE', 'ZAMOWIONE', 'CZESIOWO_DOSTARCZONE'
    # ana["CZEKA_NA_SPAKOWANIE_obj"] = (ana.CZEKA_NA_SPAKOWANIE * ana.obj)
    # ana["CZESCIOWO_DOSTARCZONE_obj"] = (ana.CZESIOWO_DOSTARCZONE * ana.obj)

    self.ar = ana[kol_MAX[1:]]
    self.ar_skr = ana[kol_skr[1:]]
    self.bryly_do_zamowienia = ana[["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]
    self.analiza_obj = ana[[x for x in ana.columns if "obj" in x][1:]].sum()


    war_zagr = (self.ar.WOLNE_SALDO < self.ar.MIN) & (self.ar.WOLNE_SALDO >= 0)
    self.zagrozone = self.ar[war_zagr][["OPIS", "ZAMOWIONE", "SALDO", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "MIN", "WOLNE_SALDO"]]

    self.krytyczne = self.ar[(self.ar.WOLNE_SALDO < 0)][["OPIS", "ZAMOWIONE","CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN"]+kol_2+["WST", "WOLNE_SALDO"]]

  def Bryly_do_zamowienia(self, wszystkie_bryly=False, zerowe_zam=False, lista_korekty_zam = False, korekta_zam:dict=None):
    """
    wszytkie_bryly -> zwraca tabele z wszystkimi bryłami w analize
    zerowe_zam -> ustawia kolumne z zerowymi ilościami zamówienia dal wszytkich brył w analizie
    lista_korekty_zam -> zwraca dict z bryłami ustawionymi do zamówienia
    karekta_zam -> dict z poporawionymi ilościami zamówień brył, funkcja zwróci DF z bryłami z analizy oraz podsymowanie pianek do VITA
    """

    if wszystkie_bryly:
      bdz = self.bryly_do_zamowienia
    else:
      bdz = self.bryly_do_zamowienia[self.bryly_do_zamowienia.DO_ZAM_SZT > 0][["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]

    if zerowe_zam:
      bdz["zero_zam"] = 0
      return bdz[["KOD", "OPIS", "BRYLA_GEN", "zero_zam"]]

    if lista_korekty_zam:
      return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()}

    if korekta_zam:
      kor = pd.DataFrame(korekta_zam.values(), columns=["KOREKTA_ZAM"], index=list(korekta_zam.keys())).reset_index().rename(columns={"index": "BRYLA_GEN"})
      kor_zam = bdz.merge(kor, how="right", on="BRYLA_GEN")[["KOD", "OPIS", "BRYLA_GEN", "KOREKTA_ZAM"]]
      bryly_kor_zam = {i[1].BRYLA_GEN: i[1].KOREKTA_ZAM for i in kor_zam[["BRYLA_GEN", "KOREKTA_ZAM"]].iterrows()}
      cls = self.klasa(bryly_kor_zam)
      # print(cls)
      return kor_zam[[ "KOD", "OPIS",  "KOREKTA_ZAM"]].rename(columns={"KOREKTA_ZAM": "DO_ZAMOWIENIA"}), cls

    return bdz, self.klasa({i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()})

  def Wykres_podsumowanie_obj(self, nazwa_modelu=True):
    dane_zam = self.analiza_obj
    labels = dane_zam.index.to_list()
    values = dane_zam.values

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    if nazwa_modelu:
      fig.update_layout(
          title=f"{self.MODEL}: STOSUNKI OBIETOSCI",
          )
    else:
      fig.update_layout(
          title=f"STOSUNKI OBIETOSCI",
          )

    fig.show()


  def Wekres_obj(self, nazwa_modelu=True):
    analiza_obj = analiza[analiza.RODZINA_NAZWA == self.MODEL[:3]][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]

    bryly = analiza_obj["OPIS"].to_list()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.SALDO_obj.to_list(),
        name="SALDO_obj"
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.ZAMOWIONE_obj.to_list(),
        name="ZAMOWIONE_obj"
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.MAX_obj.to_list(),
        name="MAX_obj"
    ))

    if nazwa_modelu:
      fig.update_layout(
          title=f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3")
    else:
      fig.update_layout(
          title=f"OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3")

    fig.show()

  def Raport(self, prt=None):
    """
    prt = prtW -> drukuje raport z wykresami
    prt = prt -> drukuje raport
    prt = None -> zwraca dict z raportem brakow
    """
    bdz = self.Bryly_do_zamowienia()[1]

    if prt == "prtW":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {self.ar.DO_ZAM_SZT.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

      self.Wekres_obj(False)
      print("------------------------------------------------------------------")
      self.Wykres_podsumowanie_obj(False)

    elif prt == "prt":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {self.ar.DO_ZAM_SZT.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

    else:
      return {"MODEL": self.MODEL,
              "POZYCJE_ZAGROZONE": self.zagrozone.shape[0],
              "BRAKI": self.krytyczne.shape[0],
              "ILOSC_BRAKOW": abs(self.krytyczne.WOLNE_SALDO.sum()),
              "BRYL_DO_ZAMOWIENIA": self.ar.DO_ZAM_SZT.sum(),
              "OBJ_BRYL_DO_ZAM_DO_OBJ_MAX": (self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj),
              "OBJ_CIECH": bdz.ciech_VOL,
              "OBJ_VITA": bdz.vita_VOL,
              "OBJ_PIANPOL": bdz.pianpol_VOL
              }




