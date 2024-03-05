import pandas as pd
import numpy as np
from Modele_pianek.Pianki import Pianki
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


