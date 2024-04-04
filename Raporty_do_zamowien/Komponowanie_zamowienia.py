from Modele_db.modele_db import *
from Analiza_pianek.owaty import *
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


def Raport_zamowionych_pianek_i_owat(tabele_zamowien=list, nazwa_pliku_xlsx=None):
  zapotrzebowanie_na_owaty(oblicz_owaty_do_zamowienia(tabele_zamowien),[])

  if nazwa_pliku_xlsx:
    pd.concat(tabele_zamowien).merge(
        oblicz_owaty_do_zamowienia(tabele_zamowien)[["KOD", "O1", "O2", "O3", "L1","W3"]].fillna(0),
        how="left",
        on="KOD").rename(columns={"O1":"ZIELONA", "O2":"NIEBIESKA", "O3":"CZERWONA", "L1":"ŻÓŁTA"}).to_excel(nazwa_pliku_xlsx)
  else:
    return  pd.concat(tabele_zamowien).merge(
        oblicz_owaty_do_zamowienia(tabele_zamowien)[["KOD", "O1", "O2", "O3", "L1","W3"]].fillna(0),
        how="left",
        on="KOD").rename(columns={"O1":"ZIELONA", "O2":"NIEBIESKA", "O3":"CZERWONA", "L1":"ŻÓŁTA"})




# Dodaj_pozycje_do_ZAM_PIANKI(2414, "P", "1_24", zwil, wil, "24/0382", nr_partii="14/01,")#, DODAJ_DO_BAZY=True)
#Dodaj_pozycje_do_ZAM_PIANKI(2412, "P", "2_24", zrev, rev, "24/0347", nr_partii="12/01,")#, DODAJ_DO_BAZY=True)

# def Utwoz_klase_modelu_pianek_z_bazy_ZAM_PIANKI():
#   with engine.begin() as conn:
#     zp = pd.read_sql(text(""))
