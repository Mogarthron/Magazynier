from Modele_db import *
import pandas as pd
import numpy as np

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
    lt = list() #lista tabel pianek dla karzdej bryły w madelu
    lista_opisowa = list()

    # self.tab = self.tab[self.tab.BRYLA.isin(list(bryly.keys()))]

    for i in bryly:
      lt.append(self.__bryla_pianki(i, bryly[i]))

    def vol(N, i):
      _vol = self.tab[self.tab.NUMER == N][["WYS", "SZER", "DLUG"]].drop_duplicates()
      return i * _vol["WYS"].values[0] * _vol["SZER"].values[0] * _vol["DLUG"].values[0] / 1000_000_000

    if len(lt) > 0:
      pianki = pd.concat(lt).groupby("NUMER").sum().reset_index()[["NUMER", "ilosc"]]
      try:
        pianki["VOL"] = pianki.apply(lambda x: vol(x.NUMER, x.ilosc), axis=1)
      except:
        print(f"VOL 0!! {self.MODEL}")
        pianki["VOL"] = np.zeros(pianki.shape[1])
    else:
      pianki = pd.DataFrame(data=[["ND", 0, "ND", "ND", "ND", "ND", "ND", 0] for x in range(8)], columns=['NUMER', 'ilosc', 'TYP', 'PROFIL', 'OZN', 'OPIS', 'WYMIAR', 'VOL'])
      

    for n in pianki.NUMER.index:
      t = self.tab[self.tab.NUMER == pianki.NUMER.iloc[n]]
      num = pianki.NUMER.iloc[n]
      typ = t.TYP.unique()[0] if len(t) != 0 else "ND"
      profil = t.PROFIL.unique()[0] if len(t) != 0 else "ND"
      ozn = t.OZN.unique()[0] if len(t) != 0 else "ND"
      opis = t.PRZEZ.unique()[0] if len(t) != 0 else "ND"
      wymiar = t.WYMIAR.unique()[0] if len(t) != 0 else "ND"
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

    if len(lt) > 0:
      zpm = pianki.merge(pd.concat([pd.DataFrame([x[:-1] for x in lista_opisowa], columns=["NUMER", "TYP", "PROFIL", "OZN", "OPIS", "WYMIAR"]),
              pd.DataFrame(lo_b, columns=[f"br{x}" for x in range(1, maks+1)])],axis=1), how="left", on="NUMER")
    
    else:
      zpm = pianki

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
