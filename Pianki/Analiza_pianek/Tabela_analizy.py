from Modele_db.modele_db import session, ZAM_PIANKI, TRANSPORTY_POZYCJE, baza_PIANKI
import pandas as pd
import numpy as np
from Pianki.Analiza_pianek import analiza, pda
from sqlalchemy import case, func
from sqlalchemy import or_, and_
import plotly.express as px
import json
from Pianki.Analiza_pianek import session, KOMPLETY_PIANEK, NALICZONE, SALDO, WSTRZYMANE
from datetime import datetime as dt, timedelta

class Tabela_analizy():

  def __init__(self, session, model=None) -> None:
    

    self.session = session

    self.model = model

    self._analiza = None
    
    self.odswiez()

  def odswiez(self):

    with open("daty_kompletacji.json") as f:
      dkom = json.load(f)
      self.daty_kompletacji = dkom["daty_kompletacji"]
      self.plik_DANE_PIANKI = dkom["plik_dane_pianki"]
    
    _analiza = self.komplety_pianek.merge(
    right=self.saldo[["KOD", "SALDO"]], how="left", on="KOD")\
      .merge(right=self.naliczone.groupby("KOD").ZAPOT_ZLEC.sum().reset_index(), how="left", on="KOD")\
      .merge(right=self.wstrzymane, how="left", on="KOD")\
      .merge(right=self.zam_pianki.groupby("KOD")[['CZEKA_NA_SPAKOWANIE', 'ZAMOWIONE', 'CZESIOWO_DOSTARCZONE']].sum().reset_index(), how="left", on="KOD")


    #PACZKI Z ZAMÓWIENIAMI
    nal_paczki = [self.naliczone[self.naliczone.LIMIT_NAZWA == x].groupby("KOD").ZAPOT_ZLEC.sum().reset_index().rename(columns={"ZAPOT_ZLEC": "/".join(x.split("/")[1:3])}) for x in self.naliczone.LIMIT_NAZWA.unique()]

    for nal_paczka in nal_paczki:
      _analiza = _analiza.merge(nal_paczka, how="left", on="KOD")

    _analiza.rename(columns={"ILOSC": "WST", "ZAPOT_ZLEC":"ZLECENIA", "ILE_ZAMOWIONE": "ZAM"}, inplace=True)

    def do_zam_szt(max_,wolne,zam,czek_na_spak, czesiowo_dos):
      """sztuki do zamowienia"""
      s = max_ - wolne - zam - czek_na_spak - czesiowo_dos
      if s > 0:
        return s
      return 0

    _analiza.fillna(0, axis=1, inplace=True)
    _analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]] = _analiza[["MAX", "obj", "SALDO", "ZLECENIA", "WST", "CZEKA_NA_SPAKOWANIE", "ZAMOWIONE"]].astype(float)
    _analiza["MIN"] = (_analiza.MAX/2).round(0).astype(int)
    _analiza["SUMA_ZLEC"] = (_analiza.ZLECENIA + _analiza.WST)
    _analiza["SALDO_Z_NIE_SPAK"] = _analiza.SALDO + _analiza.CZEKA_NA_SPAKOWANIE
    _analiza["WOLNE_SALDO"] = (_analiza.SALDO - _analiza.SUMA_ZLEC)
    _analiza["WOLNE_NIE_SPAK"] = (_analiza.SALDO_Z_NIE_SPAK - _analiza.SUMA_ZLEC)
    _analiza["MIN_obj"] = (_analiza.MIN * _analiza.obj)
    _analiza["MAX_obj"] = (_analiza.MAX * _analiza.obj)
    _analiza["ZAMOWIONE_obj"] = (_analiza.ZAMOWIONE * _analiza.obj)
    _analiza["CZEKA_NA_SPAKOWANIE_obj"] = (_analiza.CZEKA_NA_SPAKOWANIE * _analiza.obj)
    _analiza["CZESCIOWO_DOSTARCZONE_obj"] = (_analiza.CZESIOWO_DOSTARCZONE * _analiza.obj)
    _analiza["ZAMOWIONE_NIE_PRZYJETE_obj"] = _analiza.ZAMOWIONE_obj + _analiza.CZEKA_NA_SPAKOWANIE_obj + _analiza.CZESCIOWO_DOSTARCZONE_obj
    _analiza["SALDO_obj"] = (_analiza.SALDO * _analiza.obj)
    _analiza["WOLNE_obj"] = (_analiza.WOLNE_SALDO * _analiza.obj)
    _analiza["WOLNE_NIE_SPAK_obj"] = (_analiza.WOLNE_NIE_SPAK * _analiza.obj)
    _analiza["DO_ZAM_SZT"] = _analiza.apply(lambda x: do_zam_szt(x.MAX, x.WOLNE_SALDO, x.ZAMOWIONE, x.CZEKA_NA_SPAKOWANIE, x.CZESIOWO_DOSTARCZONE), axis=1)
    _analiza["DO_ZAM_obj"] = (_analiza.DO_ZAM_SZT * _analiza.obj)

    self._analiza = _analiza

  @property
  def analiza(self):
    
    if self._analiza is None:
      self.odswiez()
    return self._analiza

  @property
  def zam_pianki(self):
   
    if self.model:
        warunek_zam_pianki = and_(ZAM_PIANKI.model == self.model, ZAM_PIANKI.data_zakonczenia == None)

    else:
      warunek_zam_pianki = (ZAM_PIANKI.data_zakonczenia == None)

    _zam_pianki = pd.DataFrame(self.session.query(ZAM_PIANKI.tydzien, 
                                                  ZAM_PIANKI.kod, 
                                                  ZAM_PIANKI.nr_kompletacji, 
                                                  ZAM_PIANKI.opis, 
                                                  ZAM_PIANKI.ile_zam, 
                                                  ZAM_PIANKI.znacznik_dostawcy, 
                                                  ZAM_PIANKI.zam1, 
                                                  ZAM_PIANKI.zam2, 
                                                  ZAM_PIANKI.potw_dos1, 
                                                  ZAM_PIANKI.potw_dos2, 
                                                  ZAM_PIANKI.status_kompletacja).filter(warunek_zam_pianki), 
                                                  columns=["TYDZIEN", "KOD", "NR_KOMPLETACJI", "OPIS", "ILE_ZAMOWIONE", "ZNACZNIK_DOSTAWCY",
                                                            "ZAM1", "ZAM2", "dos1", "dos2", "STATUS_KOMPLETACJA"])  


    def dostarczone(zd, sk):
        """
        zd -> znacznik dostawcy
        sk -> status kompletacja

        0 - nie dostarczono lub dostarczono cześciowo (dostawca nie przywiózł wszystkich brył)
        1 - dostarczono częściowo (dodtarczył tylko jeden dostawca)
        2 - czeka na spakowanie
        3 - spakowana częściowo
        9999 - błąd
        """
        if type(sk) != str:
          return 0

        if sk == np.NaN:
          return 0

        if zd == np.NaN:
          return 0
        
        statusy = ["pV", "Pv", "r.", ".r", "r", "rV", "Pr"]

        try:
          if zd == sk:
            return 2
          elif sk == "":
            return 0
          elif sk in statusy:
            return 1      
          else:
            return 1
        except:
          return 9999


    _zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']] = _zam_pianki[['ZAM1','ZAM2','STATUS_KOMPLETACJA']].fillna("")

    _zam_pianki["dostarczono"] = _zam_pianki.apply(lambda x: dostarczone(x.ZNACZNIK_DOSTAWCY, x.STATUS_KOMPLETACJA), axis=1)

    _zam_pianki['CZEKA_NA_SPAKOWANIE'] = np.where(_zam_pianki['dostarczono'] == 2, _zam_pianki['ILE_ZAMOWIONE'], 0)
    _zam_pianki['CZESIOWO_DOSTARCZONE'] = np.where(_zam_pianki['dostarczono'] == 1, _zam_pianki['ILE_ZAMOWIONE'], 0)
    _zam_pianki['ZAMOWIONE'] = np.where((_zam_pianki['STATUS_KOMPLETACJA'] == "") & (~_zam_pianki['ZNACZNIK_DOSTAWCY'].isna()), _zam_pianki['ILE_ZAMOWIONE'], 0)
    
    return _zam_pianki

  @property
  def komplety_pianek(self):
    
    if self.model:
      warunek_komplety_pianek = and_(KOMPLETY_PIANEK.opis.like(f"%{self.model}%"),KOMPLETY_PIANEK.stan_max > 0)
    else:
      warunek_komplety_pianek = (KOMPLETY_PIANEK.stan_max > 0)

    _komplety_pianek = pd.DataFrame(session.query(KOMPLETY_PIANEK.kod, 
                                                 KOMPLETY_PIANEK.opis, 
                                                 KOMPLETY_PIANEK.czy_bryla, 
                                                 KOMPLETY_PIANEK.bryla_gen, 
                                                 KOMPLETY_PIANEK.stan_max, 
                                                 KOMPLETY_PIANEK.obj).filter(warunek_komplety_pianek), 
                                                 columns=["KOD", "OPIS", "CZY_BRYLA", "BRYLA_GEN", "MAX", "obj"])
                                             

    _komplety_pianek['CZY_BRYLA'] = _komplety_pianek['CZY_BRYLA'].fillna(1)
    _komplety_pianek['BRYLA_GEN'] = _komplety_pianek['BRYLA_GEN'].fillna("").astype(str).apply(lambda x: x.replace(".", ","))
    _komplety_pianek["RODZINA_NAZWA"] = _komplety_pianek.OPIS.apply(lambda x: x[:3])
    
    
    return _komplety_pianek

  @property
  def saldo(self):    
    return pd.DataFrame(self.session.query(SALDO.kod, SALDO.stan).all(), 
                         columns=["KOD", "SALDO"])
  
  @property
  def naliczone(self):
    return pd.DataFrame(self.session.query(NALICZONE.limit_nazwa, 
                                           NALICZONE.kod, 
                                           NALICZONE.zapot_zlec, 
                                           NALICZONE.limit_data_prod), 
                                           columns=["LIMIT_NAZWA", "KOD", "ZAPOT_ZLEC", "LIMIT_DATA_PROD"])

  @property
  def wstrzymane(self):
    return pd.DataFrame(self.session.query(WSTRZYMANE.kod, WSTRZYMANE.ilosc), 
                              columns=["KOD", "ILOSC"]).drop_duplicates("KOD")

  def Ogolna_analiza_objetosci(self, widok = None):
    """
    zwraca lub drukuje informacje o zapełnieniu aktulaym magazynów i magazynow 'wolnych' 

    widok = None -> wydruk obietosci raportu

    widok = tabelka -> tabelka z wszystkimi objetosciami brył

    widok = podsum -> tabelka z procentowym podsumowaniem wszystkich brył

    widok = podsum_prc -> wydruk wartosci procentowych raportu
    """
    oao = self._analiza.groupby("RODZINA_NAZWA")[[x for x in self._analiza.columns if "obj" in x][1:]].sum()
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
    wzm = ((podsum.WOLNE_obj + podsum.ZAMOWIONE_obj + podsum.CZESCIOWO_DOSTARCZONE_obj + podsum.CZEKA_NA_SPAKOWANIE_obj) / podsum.MAX_obj)

  
    if widok == "tabelka":
      return oao[[x for x in oao if "obj" in x]]
    elif widok == "podsum":
      return oao[[x for x in oao if "prc" in x]]
    elif widok == "podsum_prc":
      print(f"SALDO / MAX: {sm*100:.1f}%")
      print(f"WOLNE / MAX: {wm*100:.1f}%")
      print(f"WOLNE_NIE_SPAK / MAX: {wnsm*100:.1f}%")
      print(f"ZAPEŁNIENIE MAG PO ZDJECIU {len(pda)} PACZEK RAZEM Z ZAMOWIENIAMI: {wzm*100:.1f}%")

    elif widok == "json":

      ret = dict()
      for i in podsum.index:
        ret[f"{i}"] = podsum[i]

      ret[f"SALDO / MAX"] = sm*100
      ret[f"WOLNE / MAX"] = wm*100
      ret[f"WOLNE_NIE_SPAK / MAX"] = wnsm*100
      ret[f"ZAPEŁNIENIE MAG PO ZDJECIU {len(pda)} PACZEK RAZEM Z ZAMOWIENIAMI"] = wzm*100

      return ret
    else:

      max_key_length = max(len(key) for key in podsum.index)

      for i in podsum.index:
        if len(i) < max_key_length:
          space = max_key_length - len(i)
          print(f"{i}: {''.join([' ' for x in range(space)])} {podsum[i]:.0f}")

  def Braki(self, prt=True, WOLNE="SALDO"):
    """
    drukuje lub zwataca tabelę zawierająca pozycje z tabeli analiza ze stanem wolnym poniżej zera
    """

    for k in self.daty_kompletacji:
      self.daty_kompletacji[k] = dt.strptime(self.daty_kompletacji[k], "%Y-%m-%d")

    data_WST = self.daty_kompletacji[list(self.daty_kompletacji.keys())[-1]] + timedelta(7)



    pda = list(self.daty_kompletacji.keys())
    
    kol_2 = pda + ["WST"]

    if WOLNE == "SALDO":
      kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO", "WOLNE_SALDO"]
      kol_braki = ["OPIS","WOLNE_SALDO", "SALDO", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
      braki = self._analiza[self._analiza.WOLNE_SALDO < 0][kol_1+kol_2]
      braki["ZAMOWIONE"] =  braki.ZAMOWIONE + braki.CZEKA_NA_SPAKOWANIE + braki.CZESIOWO_DOSTARCZONE
      saldo = braki.SALDO.to_numpy()

      suma_brakow = "WOLNE_SALDO"

    if WOLNE == "NIE_SPAK":
      kol_1 = ["OPIS", "ZAMOWIONE", "CZEKA_NA_SPAKOWANIE", "CZESIOWO_DOSTARCZONE","SALDO_Z_NIE_SPAK", "WOLNE_NIE_SPAK"]
      kol_braki = ["OPIS","WOLNE_NIE_SPAK", "SALDO_Z_NIE_SPAK", "PACZKA", "DATA_KOMPLETACJI", "ZAMOWIONE"]
      braki = self._analiza[self._analiza.WOLNE_NIE_SPAK < 0][kol_1+kol_2]
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
      if x in list(self.daty_kompletacji.keys()):

        return self.daty_kompletacji[x]

      else:
        return data_WST

    braki["DATA_KOMPLETACJI"] = braki.PACZKA.apply(data_kompletacji)#.dt.strftime("%Y-%m-%d")
    # braki.set_index(pd.Index([x for x in range(1, braki.shape[0]+1)]),inplace=True)

    lista_brakujacych_modeli = braki.OPIS
    zp = self.zam_pianki[(~self.zam_pianki.STATUS_KOMPLETACJA.str.contains('ZAKONCZONO'))&(self.zam_pianki.OPIS.isin(lista_brakujacych_modeli))][
                                                                                        ["OPIS", "ILE_ZAMOWIONE","ZNACZNIK_DOSTAWCY", "STATUS_KOMPLETACJA", "dos1", "dos2", "dostarczono"]]
                                                                              
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

  def Zagrozone(self, prt=True, WOLNE="SALDO"):
    """
    Drukuje lub zwraca informacje o ilosci pozycji w tabeli analiza gdzie wolne znajduną sie poniżej stanu minim
    """
    if WOLNE == "SALDO":
      zagr = self._analiza[(self._analiza.WOLNE_SALDO >= 0) & (self._analiza.WOLNE_SALDO < self._analiza.MIN)][["OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE","SALDO", "MIN", "WOLNE_SALDO"]]
    if WOLNE == "NIE_SPAK":
      zagr = self._analiza[(self._analiza.WOLNE_NIE_SPAK >= 0) & (self._analiza.WOLNE_NIE_SPAK < self._analiza.MIN)][["OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "SALDO_Z_NIE_SPAK", "MIN", "WOLNE_NIE_SPAK"]]


    zagr_nie_zam = zagr[(zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE + zagr.CZESIOWO_DOSTARCZONE) == 0]

    if prt:
      print(f"WOLNE PONIZEJ MIN: {zagr.shape[0]} POZYCJE")
      print(f"WOLNE PONIZEJ MIN NIE ZAMOWIONE: {zagr_nie_zam.shape[0]} POZYCJE")
      print(f"SALDO PONIZEJ MIN: {zagr[zagr.SALDO < zagr.MIN].shape[0]} POZYCJE")
      print(f"SALDO PONIZEJ MIN NIE ZAMOWIONE: {zagr[((zagr.ZAMOWIONE + zagr.CZEKA_NA_SPAKOWANIE + zagr.CZESIOWO_DOSTARCZONE) == 0)&(zagr.SALDO < zagr.MIN)].shape[0]} POZYCJE")
    else:
      return zagr

  def Podsumowanie_paczek_i_Pw(self, nr_pw, json=False) -> json:
    """
    !!FUNKCJA NIE AKTYWNA!!

    Drukuje informacje o obiętosci paczek z owatami i obietosci spakowanych pianek dla podanych pw

    nr_pw -> numery pw przyjete w czasie analizy np: '24/12,24/14'
    """
    return "FUNKCJa W BUDOWIE!!"

  def Wykres_propozycji_zamowien(self, linia_pozioma=0.2):
    oao = self.Ogolna_analiza_objetosci("podsum").reset_index()


    fig = px.bar(oao, x="RODZINA_NAZWA", y="DO_ZAM_prc",
                title="OBIETOŚĆ BRYL DO ZAMOWIENIA DO MAKSYMALNEGO SALDA",
                hover_data=["ZAM_I_WOLNE_prc"])

    fig.add_hline(y=linia_pozioma)
    fig.show()