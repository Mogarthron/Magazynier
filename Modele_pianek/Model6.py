import pandas as pd
import numpy as np
from Modele_pianek.Pianki import Pianki
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


