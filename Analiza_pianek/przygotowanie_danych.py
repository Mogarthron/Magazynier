from Analiza_pianek import *
from modele_db import engine, text
import pandas as pd

#@title PRZYGOTOWANIE DANYCH

#PLIKI ZAM_PIANKI
komplety_pianek = pd.read_excel(zam_pianki_link, sheet_name="Arkusz3")
komplety_pianek['CZY_BRYLA'] = komplety_pianek['CZY_BRYLA'].fillna(1)
komplety_pianek['BRYLA_GEN'] = komplety_pianek['BRYLA_GEN'].fillna("").astype(str).apply(lambda x: x.replace(".", ","))
komplety_pianek["RODZINA_NAZWA"] = komplety_pianek.OPIS.apply(lambda x: x[:3])


with engine.begin() as conn:
  zam_pianki = pd.read_sql(text("""SELECT TYDZIEN, KOD, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY,
                      ZAM1, ZAM2, POTW_DATA_DOS_1 as dos1, POTW_DATA_DOS_2 as dos2, STATUS_KOMPLETACJA, UWAGI from ZAM_PIANKI WHERE STATUS_KOMPLETACJA IS NOT '1'"""), conn)


def dostarczone(x, y):
    """
    0 - nie dostarczono
    1 - dostarczono częściowo (dodtarczył tylko jeden dostawca)
    2 - czeka na spakowanie
    3 - spakowana częściowo
    """
    if type(y) != str:
      return 0

    if y == np.NaN:
      return 0

    if x == np.NaN:
      return 0

    try:
      if len(x) == len(y):
        return 2
      elif y == "":
        return 0
      else:
        return 1
    except:
      return 9999


zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']] = zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']].fillna("")

zam_pianki["dostarczono"] = zam_pianki.apply(lambda x: dostarczone(x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA), axis=1)


zam_nie_spakowane = zam_pianki[(zam_pianki.dostarczono == 2)]
zam_nie_spakowane.rename(columns={"ILE_ZAMOWIONE": "CZEKA_NA_SPAKOWANIE"}, inplace=True)
pianki_czesciowo_dostarczone = zam_pianki[(zam_pianki.dostarczono == 1)]
pianki_czesciowo_dostarczone.rename(columns={"ILE_ZAMOWIONE": "CZESIOWO_DOSTARCZONE"}, inplace=True)
pianki_w_drodze = zam_pianki[(zam_pianki.STATUS_KOMPLETACJA == "") & (~zam_pianki.ZNACZNIK_DOSTAWCY.isna())]
pianki_w_drodze.rename(columns={"ILE_ZAMOWIONE": "ZAMOWIONE"}, inplace=True)

#PLIK DANE_PIANKI_XXXX
saldo = pd.read_excel(path_dane_pianki, sheet_name="SALDO", usecols="B,D,H")
naliczone = pd.read_excel(path_dane_pianki, sheet_name="NALICZONE", usecols="C,F,Y,Z,AK").query(f"LIMIT_NAZWA.str.contains('{'|'.join(pda)}')", engine='python')
wstrzymane = pd.read_excel(path_dane_pianki, sheet_name="ZLECENIA")#.query("KOD.str.contains('16.')", engine='python')

#PACZKI Z ZAMÓWIENIAMI
nal_paczki = [naliczone[naliczone.LIMIT_NAZWA == x].groupby("KOD_ART").ZAPOTRZ.sum().reset_index().rename(columns={"KOD_ART": "KOD", "ZAPOTRZ": "/".join(x.split("/")[1:3])}) for x in naliczone.LIMIT_NAZWA.unique()]
