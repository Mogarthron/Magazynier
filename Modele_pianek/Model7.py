import pandas as pd
import numpy as np
from Modele_pianek.Pianki import Pianki
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
