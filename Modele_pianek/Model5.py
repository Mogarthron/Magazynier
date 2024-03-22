import pandas as pd
import numpy as np
from Modele_pianek.Pianki import Pianki
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
    self.ciech = None
    self.olta = self.zpm[~filtr_pianpol]
    self.pianpol = self.zpm[filtr_pianpol]
    self.vita_VOL = 0
    self.ciech_VOL = 0
    self.olta_VOL = self.olta.VOL.sum()
    self.pianpol_VOL = self.pianpol.VOL.sum()

  def __repr__(self):
    return f"{self.MODEL} Vol Pianpol: {self.pianpol_VOL:.2f}m3, {self.MODEL} Vol OLTA: {self.olta_VOL:.2f}m3"
