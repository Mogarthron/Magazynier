import pandas as pd
import numpy as np
from Pianki.Modele_pianek.Pianki import Pianki

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


# class AMALFI(MODEL1):

#   mod_VOL_ciech = 0.9
#   MODEL = "AMALFI"

#   def __init__(self, b:dict, b_memory={"NW":0}):
#     super().__init__(b=b)

    # ama_mem_pianki = tab[(tab.MODEL == "AMALFI")&(tab.TYP == "G-401")&(tab.BRYLA.isin(["[RS", "RS]", "NW", "WN", "[LA", "LA]"]))]

