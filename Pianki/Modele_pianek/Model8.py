import pandas as pd
import numpy as np
from Pianki.Modele_pianek.Pianki import Pianki
# @title KLASY PIANEK M7

class MODEL8(Pianki):
  """
  MODEL8 pianki zamawioane w VITA razem z MEMORY
  """
  mod_VOL_pianpol = 1
  mod_VOL_vita = 1

  MODEL = ""

  def __init__(self, b:dict):
    super().__init__(MODEL=self.MODEL, galanteria="V", siedziska_HR="V", leniwa="V")

    self.bryly = {k:v for k,v in b.items() if b[k] != 0}

    self.zpm = self.zestawienie_pianek_modelu(b)
    # filtr_vita = (self.zpm.TYP != "G-401")
    self.vita = self.zpm#[filtr_vita]
    self.ciech = None
    self.pianpol = None
    self.vita_VOL = self.vita.VOL.sum()*self.mod_VOL_vita
    self.ciech_VOL = 0
    self.pianpol_VOL = 0

  def __repr__(self):
    return f"{self.MODEL} Vol Vita: {self.vita_VOL:.2f}m3"
