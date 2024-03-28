import pandas as pd
import numpy as np
import plotly.express as px

from Analiza_pianek import *
from Modele_db import *


def Ogolna_analiza_objetosci(widok = None):
  """
  zwraca lub drukuje informacje o zapełnieniu aktulaym magazynów i magazynow 'wolnych' 

  widok = None -> wydruk obietosci raportu

  widok = tabelka -> tabelka z wszystkimi objetosciami brył

  widok = podsum -> tabelka z procentowym podsumowaniem wszystkich brył

  widok = podsum_prc -> wydruk wartosci procentowych raportu
  """
  oao = analiza.groupby("RODZINA_NAZWA")[[x for x in analiza.columns if "obj" in x][1:]].sum()
  oao["SALDO_MAX_prc"] = oao.SALDO_obj / oao.MAX_obj
  oao["WOLNE_MAX_prc"] = oao.WOLNE_obj / oao.MAX_obj
  oao["WOLNE_NIE_SPAK_MAX_prc"] = oao.WOLNE_NIE_SPAK_obj / oao.MAX_obj
  oao["ZAM_I_WOLNE_prc"] = (oao.WOLNE_obj + oao.ZAMOWIONE_obj) / oao.MAX_obj
  oao["DO_ZAM_prc"] = (oao.DO_ZAM_obj / oao.MAX_obj)

  podsum = oao[[x for x in oao if "obj" in x]].sum()

  for c in podsum.index:
    podsum[c] = np.round(podsum[c], 2)
  
  sm = (podsum.SALDO_obj / podsum.MAX_obj)
  wm = (podsum.WOLNE_obj / podsum.MAX_obj)
  wnsm = (podsum.WOLNE_NIE_SPAK_obj / podsum.MAX_obj)
  wzm = ((podsum.WOLNE_obj + podsum.ZAMOWIONE_obj+podsum.CZEKA_NA_SPAKOWANIE_obj) / podsum.MAX_obj)

  if widok == "tabelka":
    return oao[[x for x in oao if "obj" in x]]
  elif widok == "podsum":
    return oao[[x for x in oao if "prc" in x]]
  elif widok == "podsum_prc":
    print(f"SALDO / MAX: {sm*100:.1f}%")
    print(f"WOLNE / MAX: {wm*100:.1f}%")
    print(f"WOLNE_NIE_SPAK / MAX: {wnsm*100:.1f}%")
    print(f"ZAPEŁNIENIE MAG PO ZDJECIU {len(pda)} PACZEK RAZEM Z ZAMOWIENIAMI: {wzm*100:.1f}%")
  else:

    max_key_length = max(len(key) for key in podsum.index)

    for i in podsum.index:
      if len(i) < max_key_length:
        space = max_key_length - len(i)
        print(f"{i}: {''.join([' ' for x in range(space)])} {podsum[i]:.0f}")



def Braki(prt=True, WOLNE="SALDO"):
  """
  drukuje lub zwataca tabelę zawierająca pozycje z tabeli analiza ze stanem wolnym poniżej zera
  """

  kol_2 = pda + ["WST"]

  if WOLNE == "SALDO":
    kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO", "WOLNE_SALDO"]
    kol_braki = ["OPIS","WOLNE_SALDO", "SALDO", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_SALDO < 0][kol_1+kol_2]
    braki["ZAMOWIONE"] =  braki.ZAMOWIONE + braki.CZEKA_NA_SPAKOWANIE + braki.CZESIOWO_DOSTARCZONE
    saldo = braki.SALDO.to_numpy()

    suma_brakow = "WOLNE_SALDO"

  if WOLNE == "NIE_SPAK":
    kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO_Z_NIE_SPAK", "WOLNE_NIE_SPAK"]
    kol_braki = ["OPIS","WOLNE_NIE_SPAK", "SALDO_Z_NIE_SPAK", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
    braki = analiza[analiza.WOLNE_NIE_SPAK < 0][kol_1+kol_2]
    # braki["ZAMOWIONE"] =  braki.ZAMOWIONE + braki.CZEKA_NA_SPAKOWANIE + braki.CZESIOWO_DOSTARCZONE
    saldo = braki.SALDO_Z_NIE_SPAK.to_numpy()

    suma_brakow = "WOLNE_NIE_SPAK"

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
  zp = zam_pianki[(zam_pianki.STATUS_KOMPLETACJA != 'ZAKONCZONO')&(zam_pianki.OPIS.isin(lista_brakujacych_modeli))][["OPIS", "ILE_ZAMOWIONE","ZNACZNIK_DOSTAWCY", "STATUS_KOMPLETACJA", "dos1", "dos2", "dostarczono"]]
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
  # print(braki.columns)
  return braki[kol_braki+["UWAGI", "GRUPA"]], {"POZYCJE": braki.shape[0], "ILOSC_BAKOW": abs(braki[suma_brakow].sum())}

def Zagrozone(prt=True, WOLNE="SALDO"):
  """
  Drukuje lub zwraca informacje o ilosci pozycji w tabeli analiza gdzie wolne znajduną sie poniżej stanu minim
  """
  if WOLNE == "SALDO":
    zagr = analiza[(analiza.WOLNE_SALDO >= 0) & (analiza.WOLNE_SALDO < analiza.MIN)][["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE","SALDO", "MIN", "WOLNE_SALDO"]]
  if WOLNE == "NIE_SPAK":
    zagr = analiza[(analiza.WOLNE_NIE_SPAK >= 0) & (analiza.WOLNE_NIE_SPAK < analiza.MIN)][["OPIS", "ZAMOWIONE", "SALDO_Z_NIE_SPAK", "MIN", "WOLNE_NIE_SPAK"]]


  zagr_nie_zam = zagr[(zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0]

  if prt:
    print(f"WOLNE PONIZEJ MIN: {zagr.shape[0]} POZYCJE")
    print(f"WOLNE PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE")
    print(f"SALDO PONIZEJ MIN: {zagr[zagr.SALDO < zagr.MIN].shape[0]} POZYCJE")
    print(f"SALDO PONIZEJ MIN NIE ZAMOWIONE: {zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE) == 0)&(zagr.SALDO < zagr.MIN)].shape[0]} POZYCJE")
  else:
   return zagr


def Podsumowanie_paczek_i_Pw(nr_pw) -> None:
  """
  Drukuje informacje o obiętosci paczek z owatami i obietosci spakowanych pianek dla podanych pw

  nr_pw -> numery pw przyjete w czasie analizy np: '24/12|24/14'
  """
 
  pw = pd.read_excel(zam_pianki_link, sheet_name="PW")
  pw= pw[pw.PW.str.contains(nr_pw)].merge(komplety_pianek[["KOD", "obj"]], how="left", on="KOD")
  pw["SPAKOWANE_M3"] = pw.ILOSC * pw.obj

  print("OBIĘTOSC PACZEK (Z OWATAMI)")
  sum_obj = 0
  for p in pda:
    p_obj = (analiza[p]*analiza.obj).sum()
    sum_obj += p_obj
    print(f"{p}: {p_obj:.0f}m3")


  print(f"WST: {(analiza.WST*analiza.obj).sum():.0f}m3")
  print(f"Objetość wszystkich paczek: {sum_obj + (analiza.WST*analiza.obj).sum():.0f}m3")
  print(f"PW {nr_pw} spakowano: {pw.SPAKOWANE_M3.sum():.0f}M3")


def Wykres_propozycji_zamowien():
  oao = Ogolna_analiza_objetosci("podsum").reset_index()


  fig = px.bar(oao, x="RODZINA_NAZWA", y="DO_ZAM_prc",
              title="OBIETOŚĆ BRYL DO ZAMOWIENIA DO MAKSYMALNEGO SALDA",
              hover_data=["ZAM_I_WOLNE_prc"])

  fig.add_hline(y=.2)
  fig.show()


