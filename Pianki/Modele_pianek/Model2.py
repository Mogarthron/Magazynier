import pandas as pd
import numpy as np
from Pianki.Modele_pianek.Pianki import Pianki
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


