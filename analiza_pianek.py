from datetime import datetime as dt, timedelta
import pandas as pd
import numpy as np
import json

from modele_db import *

import warnings
warnings.filterwarnings('ignore')

with open("./linki.json") as f:
  linki = json.load(f)
  path_dane_pianki = linki["path_dane_pianki"]
  owaty_linki = linki["owaty"]
  zam_pianki_link = linki["zam_pianki_link"]

print(linki)

#daty kompletacji
daty_kompletacji = {
                    # "04/03":dt(2024,2,14),
                    # "05/03":dt(2024,2,21),
                    # "05/05":dt(2024,2,21),
                    "05/01":dt(2024,2,28),
                    "06/01":dt(2024,3,6),
                    "07/01":dt(2024,3,13),
                    "08/01":dt(2024,3,20),
                    "09/01":dt(2024,3,27),
                    }

# data_WST = dt.strptime(daty_kompletacji[list(daty_kompletacji.keys())[-1]], "%Y-%m-%d") + timedelta(7)
data_WST = daty_kompletacji[list(daty_kompletacji.keys())[-1]] + timedelta(7)
# print(data_WST)

pda = list(daty_kompletacji.keys())



#@title OWATY
_owaty = pd.read_excel(owaty_linki, sheet_name="Arkusz1")

#w zamowieniu podajemy ilosc belek, na FV dostajemy całkwitą ilosc metrów kwadratowych dla danego typu

ozn_owat = {                  #g/m2, szer, mb
    "O1": ["B/16/150 (1.6x50)", 150, 1.6, 50, "zielona"],
    "O2": ["B/16/200 (1.2x40)", 200, 1.2, 40, "niebieska"],
    "O3": ["B/16/200 (1.6x40)", 200, 1.6, 40, "czerwona"],
}
# wyjatki
# ama 3,5 uważać!!
# hud NW
# wil uważać!!!
# hor 3
# hor 3,5
# sto z50
# sto z70
# sto 3,5
# max z70
# max z60
# oxy 5

def wyczysc_zuzcie(x):
  if type(x) == float:
    return x
  elif type(x) == int:
    return float(x)

  x = x.rstrip()
  if x[-1] == ".":
    x = x[:-1]

  try:
    return float(x)
  except:
    return 99999.0

_owaty["ZUZYCIE"] = _owaty.ZUZYCIE_mb.apply(wyczysc_zuzcie)
_owaty["TYP_OWATY"] = _owaty.NAZWA_UKL.apply(lambda x: x[:2].replace("0", "O"))
_owaty["RODZINA_NAZWA"] = _owaty.OPIS.fillna("BRAK").apply(lambda x: x[:3])

typy_owat = _owaty.TYP_OWATY.unique()


ltypy = list()
for t in typy_owat:
  df = _owaty[(_owaty.TYP_OWATY == t)&(_owaty.RODZINA_NAZWA != "BRA")]
  df.rename(columns={"ZUZYCIE": t}, inplace=True)
  ltypy.append(df[["OPIS", t]])

owaty = ltypy[0]
for t in ltypy[1:]:
  owaty = owaty.merge(t, how="outer", on="OPIS").fillna(0)

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


#@title TABELA analiza
analiza = komplety_pianek.merge(
    right=saldo[["KOD","SALDO"]], how="left", on="KOD").merge(
    right=naliczone.groupby("KOD_ART").sum().reset_index(), how="left", left_on="KOD", right_on="KOD_ART").merge(
    right=wstrzymane, how="left", on="KOD").merge(
    right=zam_nie_spakowane.groupby("KOD").sum()["CZEKA_NA_SPAKOWANIE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_w_drodze.groupby("KOD").sum()["ZAMOWIONE"].reset_index(), how="left", on="KOD").merge(
    right=pianki_czesciowo_dostarczone.groupby("KOD").sum()["CZESIOWO_DOSTARCZONE"].reset_index(), how="left", on="KOD")

for nal_paczka in nal_paczki:
  analiza = analiza.merge(nal_paczka, how="left", on="KOD")

analiza.rename(columns={"ILOSC": "WST", "ZAPOTRZ":"ZLECENIA", "ILE_ZAMOWIONE": "ZAM"}, inplace=True)

def do_zam_szt(m,w,zam,czek_na_spak, czesiowo_dos):
  s = m-w-zam - czek_na_spak - czesiowo_dos
  if s > 0:
    return s
  return 0

analiza.drop("KOD_ART", axis=1, inplace=True)
analiza.fillna(0, axis=1, inplace=True)
analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]] = analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]].astype(float)

analiza["MIN"] = (analiza.MAX/2).round(0).astype(int)
analiza["SUMA_ZLEC"] = (analiza.ZLECENIA + analiza.WST)
analiza["SALDO_Z_NIE_SPAK"] = analiza.SALDO + analiza.CZEKA_NA_SPAKOWANIE
analiza["WOLNE_SALDO"] = (analiza.SALDO - analiza.SUMA_ZLEC)
analiza["WOLNE_NIE_SPAK"] = (analiza.SALDO_Z_NIE_SPAK - analiza.SUMA_ZLEC)
analiza["MAX_obj"] = (analiza.MAX * analiza.obj)
analiza["ZAMOWIONE_obj"] = (analiza.ZAMOWIONE * analiza.obj)
analiza["CZEKA_NA_SPAKOWANIE_obj"] = (analiza.CZEKA_NA_SPAKOWANIE * analiza.obj)
analiza["CZESCIOWO_DOSTARCZONE_obj"] = (analiza.CZESIOWO_DOSTARCZONE * analiza.obj)
analiza["SALDO_obj"] = (analiza.SALDO * analiza.obj)
analiza["WOLNE_obj"] = (analiza.WOLNE_SALDO * analiza.obj)
analiza["WOLNE_NIE_SPAK_obj"] = (analiza.WOLNE_NIE_SPAK * analiza.obj)
analiza["DO_ZAM_SZT"] = analiza.apply(lambda x: do_zam_szt(x.MAX, x.WOLNE_SALDO, x.ZAMOWIONE, x.CZEKA_NA_SPAKOWANIE, x.CZESIOWO_DOSTARCZONE), axis=1)

analiza["DO_ZAM_obj"] = (analiza.DO_ZAM_SZT * analiza.obj)


def Ogolna_analiza_objetosci(widok = None):
  """
  widok = None -> zestawienie obietosci raportu
  widok = tabelka -> tabelka z wszystkimi objetosciami brył
  widok = podsum -> tabelka z procentowym podsumowaniem wszystkich brył
  widok = podsum_prc -> zestawienie wartosci procentowych raportu
  """
  oao = analiza.groupby("RODZINA_NAZWA")[[x for x in analiza.columns if "obj" in x][1:]].sum()
  oao["SALDO_MAX_prc"] = oao.SALDO_obj / oao.MAX_obj
  oao["WOLNE_MAX_prc"] = oao.WOLNE_obj / oao.MAX_obj
  oao["WOLNE_NIE_SPAK_MAX_prc"] = oao.WOLNE_NIE_SPAK_obj / oao.MAX_obj
  oao["ZAM_I_WOLNE_prc"] = (oao.WOLNE_obj + oao.ZAMOWIONE_obj) / oao.MAX_obj
  oao["DO_ZAM_prc"] = (oao.DO_ZAM_obj / oao.MAX_obj)

  podsum = oao[[x for x in oao if "obj" in x]].sum()
  sm = (podsum.SALDO_obj / podsum.MAX_obj)
  wm = (podsum.WOLNE_obj / podsum.MAX_obj)
  wnsm = (podsum.WOLNE_NIE_SPAK_obj / podsum.MAX_obj)
  wzm = ((podsum.WOLNE_obj + podsum.ZAMOWIONE_obj) / podsum.MAX_obj)

  if widok == "tabelka":
    return oao[[x for x in oao if "obj" in x]]
  elif widok == "podsum":
    return oao[[x for x in oao if "prc" in x]]
  elif widok == "podsum_prc":
    print(f"SALDO / MAX: {sm*100:.1f}%")
    print(f"WOLNE / MAX: {wm*100:.1f}%")
    print(f"WOLNE_NIE_SPAK / MAX: {wnsm*100:.1f}%")
    print(f"ZAPEŁNIENIE MAG PO ZDJECIU {len(pda)} PACZEK RAZEM Z ZAMOWIONYMI: {wzm*100:.1f}%")
  else:
    print(podsum)


def Braki(prt=True, WOLNE="SALDO"):

  kol_2 = pda + ["WST"]

  if WOLNE == "SALDO":
    kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO", "WOLNE_SALDO"]
    kol_braki = ["OPIS","WOLNE_SALDO", "SALDO", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_SALDO < 0][kol_1+kol_2]
    braki["ZAMOWIONE"] =  braki.ZAMOWIONE + braki.CZEKA_NA_SPAKOWANIE + braki.CZESIOWO_DOSTARCZONE
    saldo = braki.SALDO.to_numpy()

  if WOLNE == "NIE_SPAK":
    kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO_Z_NIE_SPAK", "WOLNE_NIE_SPAK"]
    kol_braki = ["OPIS","WOLNE_NIE_SPAK", "SALDO_Z_NIE_SPAK", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_NIE_SPAK < 0][kol_1+kol_2]
    # braki["ZAMOWIONE"] =  braki.ZAMOWIONE + braki.CZEKA_NA_SPAKOWANIE + braki.CZESIOWO_DOSTARCZONE
    saldo = braki.SALDO_Z_NIE_SPAK.to_numpy()

  kiedy_zabraknie = ["" for x in range(braki.shape[0])]
  sum_zlec = braki[pda[0]].to_numpy()

  saldo_po_paczce = saldo - sum_zlec
  for p in enumerate(saldo_po_paczce):
    if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
      kiedy_zabraknie[p[0]] = pda[0]

  for paczka in pda[1:]:
    saldo_po_paczce -= braki[paczka].to_numpy()
    for p in enumerate(saldo_po_paczce):
      if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
        kiedy_zabraknie[p[0]] = paczka

  saldo_po_paczce -= braki.WST.to_numpy()
  for p in enumerate(saldo_po_paczce):
    if p[1] < 0 and (kiedy_zabraknie[p[0]] == ""):
      kiedy_zabraknie[p[0]] = "WST"

  braki["PACZKA"] = kiedy_zabraknie

  def data_kompletacji(x):
    if x in list(daty_kompletacji.keys()):

      return daty_kompletacji[x]

    else:
      return data_WST

  braki["DATA_KOMPLETACJI"] = braki.PACZKA.apply(data_kompletacji)#.dt.strftime("%Y-%m-%d")
  # braki.set_index(pd.Index([x for x in range(1, braki.shape[0]+1)]),inplace=True)

  lista_brakujacych_modeli = braki.OPIS
  zp = zam_pianki[(zam_pianki.STATUS_KOMPLETACJA != '1')&(zam_pianki.OPIS.isin(lista_brakujacych_modeli))][["OPIS", "ILE_ZAMOWIONE","ZNACZNIK_DOSTAWCY", "STATUS_KOMPLETACJA", "dos1", "dos2", "dostarczono"]]
  # list(lista_brakujacych_modeli)[0]
  braki = braki.merge(zp, how="left", on="OPIS")
  braki[["dos1", "dos2"]] = braki[["dos1", "dos2"]].fillna("")
  braki["ZNACZNIK_DOSTAWCY"] = braki["ZNACZNIK_DOSTAWCY"].fillna("")
  braki["STATUS_KOMPLETACJA"] = braki["STATUS_KOMPLETACJA"].fillna("")

  braki["dos1"] = braki.dos1.apply(lambda x: x.split(">")[-1])
  braki["dos2"] = braki.dos2.apply(lambda x: x.split(">")[-1])


  def grupa(dostarczono, zd, sk, d1, d2):
    if zd == "":
      return "...", 1
    elif zd != "" and dostarczono == 0:
      return f"PIANKI ZAMOWIONE {zd}, {sk}, {d1.split('>')[0]}, {d2.split('>')[0]}", 2
    elif zd != "" and dostarczono == 1:
      return f"DOSTARCONO CZESCIOWO {zd}, {sk}, {d1.split('>')[0]}, {d2.split('>')[0]}", 3

    return "CZEKA NA SPAKOWANIE", 4

  braki["UWAGI"] = braki.apply(lambda x: grupa(x.dostarczono, x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA, x.dos1, x.dos2)[0], axis=1)
  braki["GRUPA"] = braki.apply(lambda x: grupa(x.dostarczono, x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA, x.dos1, x.dos2)[1], axis=1)
  # braki
  return braki[kol_braki+["UWAGI", "GRUPA"]], {"POZYCJE": braki.shape[0], "ILOSC_BAKOW": abs(braki[braki.columns[3]].sum())}

def Zagrozone(prt=True, WOLNE="SALDO"):
  if WOLNE == "SALDO":
    zagr = analiza[(analiza.WOLNE_SALDO >= 0) & (analiza.WOLNE_SALDO < analiza.MIN)][["OPIS", "ZAMOWIONE", "SALDO", "MIN", "WOLNE_SALDO"]]
  if WOLNE == "NIE_SPAK":
    zagr = analiza[(analiza.WOLNE_NIE_SPAK >= 0) & (analiza.WOLNE_NIE_SPAK < analiza.MIN)][["OPIS", "ZAMOWIONE", "SALDO_Z_NIE_SPAK", "MIN", "WOLNE_NIE_SPAK"]]


  zagr_nie_zam = zagr[zagr.ZAMOWIONE == 0]

  if prt:
    print(f"PONIZEJ MIN: {zagr.shape[0]} POZYCJE")
    print(f"PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE")
  else:
   return zagr


import plotly.express as px

def Wykres_propozycji_zamowien():
  oao = Ogolna_analiza_objetosci("podsum").reset_index()


  fig = px.bar(oao, x="RODZINA_NAZWA", y="DO_ZAM_prc",
              title="OBIETOŚĆ BRYL DO ZAMOWIENIA DO MAKSYMALNEGO SALDA",
              hover_data=["ZAM_I_WOLNE_prc"])

  fig.add_hline(y=.2)
  fig.show()



#@title KLASA

import plotly.graph_objects as go

class Analiza_Rodziny():
  def __init__(self, cls, grupa_sprzedarzy=1, magazyn_skladowania=2, cls2=None):

    kol_1 = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_1_MAX = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "MAX", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_2 = pda#"ZLECENIA"
    kol_3 = ["WST", "DO_ZAM_SZT"]
    kol_MAX = kol_1_MAX+kol_2+kol_3
    kol_skr = kol_1
    self.MODEL = cls.MODEL
    self.klasa = cls
    self.grupa_sprzedarzy = grupa_sprzedarzy

    if cls2:
      self.ana = analiza[analiza.RODZINA_NAZWA.str.contains(f"{cls.MODEL[:3]}|{cls2.MODEL[:3]}")]
    else:
      self.ana = analiza[analiza.RODZINA_NAZWA == cls.MODEL[:3]]

    self.ana["GRUPA_SPRZEDARZY"] = grupa_sprzedarzy

    self.ar = self.ana[kol_MAX[1:]]
    self.ar_skr = self.ana[kol_skr[1:]]
    self.bryly_do_zamowienia = self.ana[["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]
    self.analiza_obj = self.ana[[x for x in self.ana.columns if "obj" in x][1:]].sum()
    self.zamowienia = zam_pianki[zam_pianki.OPIS.str.contains(self.MODEL)]

    war_zagr = (self.ar.WOLNE_SALDO < self.ar.MIN) & (self.ar.WOLNE_SALDO >= 0)
    self.zagrozone = self.ar[war_zagr][["OPIS", "ZAMOWIONE", "SALDO", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "MIN", "WOLNE_SALDO"]]

    self.krytyczne = self.ar[(self.ar.WOLNE_SALDO < 0)][["OPIS", "ZAMOWIONE","CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN"]+kol_2+["WST", "WOLNE_SALDO"]]

  def Bryly_do_zamowienia(self, wszystkie_bryly=False, zerowe_zam=False, lista_korekty_zam = False, korekta_zam:dict=None):
    """
    wszytkie_bryly -> zwraca tabele z wszystkimi bryłami w analize
    zerowe_zam -> ustawia kolumne z zerowymi ilościami zamówienia dal wszytkich brył w analizie
    lista_korekty_zam -> zwraca dict z bryłami ustawionymi do zamówienia
    karekta_zam -> dict z poporawionymi ilościami zamówień brył, funkcja zwróci DF z bryłami z analizy oraz podsymowanie pianek do VITA
    """

    if wszystkie_bryly:
      bdz = self.bryly_do_zamowienia
    else:
      bdz = self.bryly_do_zamowienia[self.bryly_do_zamowienia.DO_ZAM_SZT > 0][["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]

    if zerowe_zam:
      bdz["zero_zam"] = 0
      return bdz[["KOD", "OPIS", "BRYLA_GEN", "zero_zam"]]

    if lista_korekty_zam:
      return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()}

    if korekta_zam:
      kor = pd.DataFrame(korekta_zam.values(), columns=["KOREKTA_ZAM"], index=list(korekta_zam.keys())).reset_index().rename(columns={"index": "BRYLA_GEN"})
      kor_zam = bdz.merge(kor, how="right", on="BRYLA_GEN")[["KOD", "OPIS", "BRYLA_GEN", "KOREKTA_ZAM"]]
      bryly_kor_zam = {i[1].BRYLA_GEN: i[1].KOREKTA_ZAM for i in kor_zam[["BRYLA_GEN", "KOREKTA_ZAM"]].iterrows()}
      cls = self.klasa(bryly_kor_zam)
      # print(cls)
      return kor_zam[[ "KOD", "OPIS",  "KOREKTA_ZAM"]].rename(columns={"KOREKTA_ZAM": "DO_ZAMOWIENIA"}), cls

    return bdz, self.klasa({i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()})

  def Wykres_podsumowanie_obj(self, nazwa_modelu=True):
    dane_zam = self.analiza_obj
    labels = dane_zam.index.to_list()
    values = dane_zam.values

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    if nazwa_modelu:
      fig.update_layout(
          title=f"{self.MODEL}: STOSUNKI OBIETOSCI",
          )
    else:
      fig.update_layout(
          title=f"STOSUNKI OBIETOSCI",
          )

    fig.show()


  def Wekres_obj(self, nazwa_modelu=True):
    analiza_obj = analiza[analiza.RODZINA_NAZWA == self.MODEL[:3]][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]

    bryly = analiza_obj["OPIS"].to_list()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.SALDO_obj.to_list(),
        name="SALDO_obj"
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.ZAMOWIONE_obj.to_list(),
        name="ZAMOWIONE_obj"
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.MAX_obj.to_list(),
        name="MAX_obj"
    ))

    if nazwa_modelu:
      fig.update_layout(
          title=f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3")
    else:
      fig.update_layout(
          title=f"OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3")

    fig.show()

  def Raport(self, prt=None):
    """
    prt = prtW -> drukuje raport z wykresami
    prt = prt -> drukuje raport
    prt = None -> zwraca dict z raportem brakow
    """
    bdz = self.Bryly_do_zamowienia()[1]
    dzs = self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT

    if prt == "prtW":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

      self.Wekres_obj(False)
      print("------------------------------------------------------------------")
      self.Wykres_podsumowanie_obj(False)

    elif prt == "prt":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

    else:
      return {"GRUPA":self.grupa_sprzedarzy,
              "MODEL": self.MODEL,
              "POZYCJE_ZAGROZONE": self.zagrozone.shape[0],
              "BRAKI": self.krytyczne.shape[0],
              "ILOSC_BRAKOW": abs(self.krytyczne.WOLNE_SALDO.sum()),
              "BRYL_DO_ZAMOWIENIA": dzs.sum(),
              "OBJ_BRYL_DO_ZAM_DO_OBJ_MAX": (self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj),
              "OBJ_CIECH": bdz.ciech_VOL,
              "OBJ_VITA": bdz.vita_VOL,
              "OBJ_PIANPOL": bdz.pianpol_VOL
              }

  def __repr__(self):
      return f"MODEL: {self.MODEL}\n"+\
            f"BRYŁ DO ZAMÓWIENIA: {self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT.sum()}szt\n"+\
            f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%"

