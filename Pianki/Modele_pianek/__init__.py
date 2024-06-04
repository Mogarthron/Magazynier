from Modele_db import *
import pandas as pd
# import numpy as np

# from modele_db import *

lista_bryl = dict()
with engine.begin() as conn:
      lb = conn.execute(text(f"SELECT * from lista_bryl_pianki"))
      tab = pd.read_sql(text("SELECT * from baza_PIANKI"), conn)

for i in lb:
  # print(i[0], i[1].split("_"))
  lista_bryl[i[0]] = [x for x in i[1].split("_")]


from Pianki.Modele_pianek.Model1 import MODEL1

class ELIXIR_CV(MODEL1):
  MODEL = "ELIXIR"
  def __init__(self,b:dict):
    super().__init__(b=b)

class AMALFI_CV(MODEL1):
  MODEL = "AMALFI"
  def __init__(self,b:dict):
    super().__init__(b=b)

class REVERSO_CV(MODEL1):
  MODEL = "REVERSO"
  def __init__(self,b=None):
    super().__init__(b=b)

class WILLOW_CV(MODEL1):
  mod_VOL_ciech = 0.95
  MODEL = "WILLOW"
  def __init__(self, b:dict):
    super().__init__(b=b)

class OXYGEN_CV(MODEL1):
  mod_VOL_ciech = 0.95
  MODEL = "OXYGEN"
  def __init__(self, b:dict):
    super().__init__(b=b)


from Pianki.Modele_pianek.Model2 import MODEL2

class HORIZON_CV(MODEL2):
  MODEL = "HORIZON"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class LOBBY_CV(MODEL2):
  MODEL = "LOBBY"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class DUO_CV(MODEL2):
  MODEL = "DUO"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class MAXWELL_CV(MODEL2):
  MODEL = "MAXWELL"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class ONYX_CV(MODEL2):
  MODEL = "ONYX"
  def __init__(self,b:dict):
    super().__init__(bg=b)

class COCO_CV(MODEL2):
  MODEL = "COCO"
  def __init__(self,b:dict):
    super().__init__(bg=b)


from Pianki.Modele_pianek.Model3 import MODEL3

class STONE_V(MODEL3):
  MODEL = "STONE"
  def __init__(self,b:dict):
    super().__init__(b=b)

class CUPIDO_V(MODEL3):
  MODEL = "CUPIDO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class UNO_V(MODEL3):
  MODEL = "UNO"
  def __init__(self,b:dict):
    super().__init__(b=b)


from Pianki.Modele_pianek.Model4 import MODEL4

class CALYPSO_C(MODEL4):
  MODEL = "CALYPSO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class DIVA_C(MODEL4):
  MODEL = "DIVA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class HUDSON_C(MODEL4):
  MODEL = "HUDSON"
  def __init__(self,b:dict):
    super().__init__(b=b)

class RITZ_C(MODEL4):
  MODEL = "RITZ"
  def __init__(self,b:dict):
    super().__init__(b=b)

class SAMOA_C(MODEL4):
  MODEL = "SAMOA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class SPECTRA_C(MODEL4):
  MODEL = "SPECTRA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class GREY_C(MODEL4):
  MODEL = "GREY"
  def __init__(self,b:dict):
    super().__init__(b=b)

class LENOX_C(MODEL4):
  MODEL = "LENOX"
  def __init__(self,b:dict):
    super().__init__(b=b)

class OVAL_C(MODEL4):
  MODEL = "OVAL"
  def __init__(self,b:dict):
    super().__init__(b=b)

class KELLY_C(MODEL4):
  MODEL = "KELLY"
  def __init__(self,b:dict):
    super().__init__(b=b)

from Pianki.Modele_pianek.Model5 import MODEL5

class AVANT_P(MODEL5):
  MODEL = "AVANT"
  def __init__(self,b:dict):
    super().__init__(b=b)

class OVAL_P(MODEL5):
  MODEL = "OVAL"
  def __init__(self,b:dict):
    super().__init__(b=b)


from Pianki.Modele_pianek.Model6 import MODEL6

class UNO_P(MODEL6):
  MODEL = "UNO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class ONYX_P(MODEL6):
  MODEL = "ONYX"
  def __init__(self,b:dict):
    super().__init__(b=b)

class DUO_P(MODEL6):
  MODEL = "DUO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class WILLOW_P(MODEL6):
  MODEL = "WILLOW"
  def __init__(self,b:dict):
    super().__init__(b=b)

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

class REVERSO_P(MODEL6):
  MODEL = "REVERSO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class DIVA_P(MODEL6):
  MODEL = "DIVA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class SAMOA_P(MODEL6):
  MODEL = "SAMOA"
  def __init__(self,b:dict):
    super().__init__(b=b)

class HUDSON_P(MODEL6):
  MODEL = "HUDSON"
  def __init__(self,b:dict):
    super().__init__(b=b)

class CALYPSO_P(MODEL6):
  MODEL = "CALYPSO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class LENOX_P(MODEL6):
  MODEL = "LENOX"
  def __init__(self,b:dict):
    super().__init__(b=b)

class COCO_P(MODEL6):
  MODEL = "COCO"
  def __init__(self,b:dict):
    super().__init__(b=b)

class GOYA_P(MODEL6):
  MODEL = "GOYA"
  def __init__(self,b:dict):
    super().__init__(b=b)

from Pianki.Modele_pianek.Model7 import MODEL7

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