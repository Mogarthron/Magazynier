import pandas as pd
import numpy as np
from Pianki.Modele_pianek.Pianki import Pianki
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


