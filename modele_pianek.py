from modele_db import *
import pandas as pd
import numpy as np

from modele_db import *
lista_bryl = dict()
with engine.begin() as conn:
      lb = conn.execute(text(f"SELECT * from lista_bryl_pianki"))
      tab = pd.read_sql(text("SELECT * from baza_PIANKI"), conn)


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

    # self.tab = self.tab[self.tab.BRYLA.isin(list(bryly.keys()))]

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


# @title KLASY PIANEK M1
class MODEL1(Pianki):
  """
  MODEL1 rozdziału pianek na siediska HR-3020 vita reszta ciech
  bm -> bryły z analizy
  bg -> bryły z generatora
  """
  mod_VOL_ciech = 1
  mod_VOL_vita = .9
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

    # ama_mem_pianki = tab[(tab.MODEL == "AMALFI")&(tab.TYP == "G-401")&(tab.BRYLA.isin(["[RS", "RS]", "NW", "WN", "[LA", "LA]"]))]

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
  mod_VOL_vita = .9
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
  mod_VOL_vita = .9
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

class CUPIDO(MODEL3):
  MODEL = "CUPIDO"
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
  mod_VOL_vita = .9
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
    return f"{self.MODEL} Vol Pianpol: {self.pianpol_VOL:.2f}m3, {self.MODEL} Vol OLTA: {self.olta_VOL:.2f}m3"


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

class AMALFI_P(MODEL6):
  MODEL = "AMALFI"
  def __init__(self,b:dict):
    super().__init__(b=b)

class STONE_P(MODEL6):
  MODEL = "STONE"
  def __init__(self,b:dict):
    super().__init__(b=b)


class ELIXIR_P(MODEL6):
  MODEL = "ELIXIR"
  def __init__(self,b:dict):
    super().__init__(b=b)

class MAXWELL_P(MODEL6):
  MODEL = "MAXWELL"
  def __init__(self,b:dict):
    super().__init__(b=b)



# @title KLASY PIANEK M7

class MODEL7(Pianki):
  """
  MODEL7 rozdział pianek Memory PIANPOL reszta VITA
  """


  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="V", siedziska_HR="V", leniwa="P")

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)
    filtr_vita = (self.zpm.TYP != "G-401")
    self.vita = self.zpm[filtr_vita]
    self.ciech = None
    self.pianpol = self.zpm[~filtr_vita]
    self.vita_VOL = self.vita.VOL.sum()
    self.ciech_VOL = 0
    self.pianpol_VOL = self.pianpol.VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Vita: {self.vita_VOL:.2f}m3, Vol Pianpol: {self.pianpol_VOL:.2f}m3"


class HORIZON_PV(MODEL7):
  MODEL = "HORIZON"
  def __init__(self,b:dict):
    super().__init__(b=b)

class ELIXIR_PV(MODEL7):
  MODEL = "ELIXIR"
  def __init__(self,b:dict):
    super().__init__(b=b)

class COCO_PV(MODEL7):
  MODEL = "COCO"
  def __init__(self,b:dict):
    super().__init__(b=b)