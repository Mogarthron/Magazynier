from modele_db import *
import pandas as pd


def oblicz_owaty_do_zamowienia(z_bdz:list):

  df_zam = pd.concat(z_bdz)
  df_zam = df_zam.merge(owaty, how="left", on="OPIS")

  for c in owaty.columns[1:]:
    df_zam[c] = df_zam[c] * df_zam.DO_ZAMOWIENIA * 1.1

  return df_zam#[owaty.columns[1:]]


def zapotrzebowanie_na_owaty(zam_owaty, wyjatki:list):
  _wyjatki = pd.Series({"O3":0, "O2":0, "O1":0, "L1":0, "W3":0})
  for w in wyjatki:
    _wyjatki += w

  zap = zam_owaty[["O3", "O2", "O1", "L1", "W3"]].sum()+_wyjatki

  # zap *= 1.1

  print(f"O1 zielona: {(zap['O1']/50).round(0):.0f} rolek")
  print(f"O2 niebieska: {(zap['O2']/40).round(0):.0f} rolek")
  print(f"O3 czerwona: {(zap['O3']/40).round(0):.0f} rolek")
  # return zap



# def pobierz_zamowienie_z_ZAM_PIANKI(tydzien, _cls):
#   _zam = zam_pianki[(zam_pianki.TYDZIEN == tydzien) & (zam_pianki.OPIS.str.contains(_cls.MODEL))].merge(komplety_pianek[["KOD", "BRYLA_GEN"]])[["OPIS", "BRYLA_GEN", "ILE_ZAMOWIONE"]]
#   return _cls({i[1].BRYLA_GEN: i[1].ILE_ZAMOWIONE for i in _zam[["BRYLA_GEN", "ILE_ZAMOWIONE"]].iterrows()})

def Utwoz_klase_modelu_pianek_z_bazy_ZAM_PIANKI():
  with engine.begin() as conn:
    zp = pd.read_sql(text(""))