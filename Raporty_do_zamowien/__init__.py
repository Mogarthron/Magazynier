import pandas as pd
import numpy as np
from modele_db import *
from Analiza_pianek import funkcje_analizy_pianek as ap, owaty as ow
from Modele_pianek import tab
from Analiza_pianek.instrukcje_zamawiana import instrukcja_zamawiania_pianpol as ar

ard = {a.MODEL: a for a in ar}
komplety_pianek = ap.komplety_pianek
zam_pianki = ap.zam_pianki
_owaty = ow._owaty

import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Border, Side
from datetime import datetime as dt

#zlecenia na kopletacje pianek i owat
def zlecenia_produkcyjne_pianki_owaty(model, nr_kompletacji, nr_partii):
  """
  nr_partii -> numer tygodnia / np.: 07/1
  """
  zp = zam_pianki[(zam_pianki.OPIS.str.contains(model))&(zam_pianki.NR_KOMPLETACJI == nr_kompletacji)][["OPIS", "ILE_ZAMOWIONE"]]

  for p in range(zp.shape[0]):

    ow = _owaty[_owaty.OPIS == zp.iloc[p].OPIS][["TYP_OWATY", "ZUZYCIE", "RODZAJ_CIECIA", "NAZWA_UKL"]].reset_index()
    ow["ZUZYCIE"] = ow.ZUZYCIE*zp.iloc[p].ILE_ZAMOWIONE*1.1
    ow["KATER_UKL"] = ow.apply(lambda x: x.NAZWA_UKL if x.RODZAJ_CIECIA == "K" else "", axis=1)

    wb = openpyxl.Workbook()
    sheet = wb.active

    sheet["A1"] = "ZLECENIE PRODUKCYJNE: WYDZIAŁ ROZKRÓJ OWAT / KOMPLETACJA OWATY"
    sheet["A3"] = f"NR PARTII: {nr_partii}"
    sheet["A4"] = f"NR ZAMÓWIENIA: {model} {nr_kompletacji}"
    sheet["A5"] = f"MODEL: {model}"
    sheet["H1"] = f"DZIEŃ WYDRUKU      {dt.now().strftime('%Y-%m-%d')}"
    sheet["E4"] = "TYP"
    sheet["F4"] = "MB"
    sheet["G4"] = "R/K"
    sheet["H4"] = "KATER_UKL"

    start_row = 5
    for r in ow.iterrows():

      sheet.cell(row=r[0]+start_row, column=5, value=r[1].TYP_OWATY)
      sheet.cell(row=r[0]+start_row, column=6, value=r[1].ZUZYCIE)
      sheet.cell(row=r[0]+start_row, column=7, value=r[1].RODZAJ_CIECIA)
      sheet.cell(row=r[0]+start_row, column=8, value=r[1].KATER_UKL)


    sheet["A15"] = "BRYŁA"
    sheet["B15"] = "ILOŚĆ PACZEK"
    sheet["C15"] = "CZAS"
    sheet["A16"] = zp.iloc[p].OPIS
    sheet["B16"] = zp.iloc[p].ILE_ZAMOWIONE

    sheet["A18"] = "UWAGI:"
    sheet["H18"] = "PODPIS, DZIEN:"

    thin = Side(border_style="thin", color="000000")
    for row in sheet[f"E4:i{ow.shape[0]+4}"]:
        for cell in row:
          cell.border = Border(bottom=thin)
    
    import os 

    path_ = f'Z:/160. ROZKRÓJ PIANEK/160.30 ZLECENIA/{model}/{model} {nr_kompletacji}/OWATY/'
    _file = f"OWATY {model} {nr_kompletacji} {zp.iloc[p].OPIS.replace(model, '').replace('/','_')}.xlsx"
    # wb.save(f"{model} {nr_kompletacji}/OWATY/OWATY {model} {nr_kompletacji} {zp.iloc[p].OPIS.replace(model, '')}.xlsx")
    if not os.path.exists(path_):
        os.makedirs(path_)

    wb.save(path_ + _file)

def zlecenia_produkcyjne_pianki_kompletacja(model, nr_kompletacji, nr_partii):
  """
  nr_partii -> numer tygodnia / np.: 07/1
  """
  zp = zam_pianki[(zam_pianki.OPIS.str.contains(model))&(zam_pianki.NR_KOMPLETACJI == nr_kompletacji)][["OPIS", "ILE_ZAMOWIONE"]]

  for p in range(zp.shape[0]):

    ow = _owaty[_owaty.OPIS == zp.iloc[p].OPIS][["TYP_OWATY", "ZUZYCIE", "RODZAJ_CIECIA", "NAZWA_UKL"]].reset_index()
    ow["ZUZYCIE"] = ow.ZUZYCIE*zp.iloc[p].ILE_ZAMOWIONE*1.1
    ow["KATER_UKL"] = ow.apply(lambda x: x.NAZWA_UKL if x.RODZAJ_CIECIA == "K" else "", axis=1)

    wb = openpyxl.Workbook()
    sheet = wb.active

    sheet["A1"] = "ZLECENIE PRODUKCYJNE: KOMPLETACJA PIANKI"
    sheet["A3"] = f"NR PARTII: {nr_partii}"
    sheet["A4"] = f"NR ZAMÓWIENIA: {model} {nr_kompletacji}"
    sheet["A5"] = f"MODEL: {model}"
    sheet["H1"] = f"DZIEŃ WYDRUKU      {dt.now().strftime('%Y-%m-%d')}"

    sheet["A15"] = "BRYŁA"
    sheet["B15"] = "ILOŚĆ PACZEK"
    sheet["C15"] = "CZAS"
    sheet["A16"] = zp.iloc[p].OPIS
    sheet["B16"] = zp.iloc[p].ILE_ZAMOWIONE

    sheet["A18"] = "UWAGI:"
    sheet["H18"] = "PODPIS, DZIEN:"

    import os 

    path_ = f'Z:/160. ROZKRÓJ PIANEK/160.30 ZLECENIA/{model}/{model} {nr_kompletacji}/KOMPLETACJA/'
    _file = f"KOMPLETACJA {model} {nr_kompletacji} {zp.iloc[p].OPIS.replace(model, '').replace('/','_')}.xlsx"


    # wb.save(f"KOMPLETACJA/KOMPLETACJA {model} {nr_kompletacji} {zp.iloc[p].OPIS.replace(model, '')}.xlsx")
    if not os.path.exists(path_):
        os.makedirs(path_)
    wb.save(path_ + _file)
    # wb.save(file_path)



#specyfikacje i zestawienie pianek w modelach do zamowień
def specyfikacja_zam_vita_xlsx(NR_zam:str, raport_vita:pd.DataFrame):
  wb = openpyxl.Workbook()
  sheet = wb.active

  sheet["B1"] = f"SPECYFIKACJA ZAMÓWIENIE DOS/{NR_zam}"
  sheet["H1"] = dt.now().strftime("%Y-%m-%d")
  sheet["B3"] = "Zamawiajacy"
  sheet["B4"] = "OLTA K.K. Zawistowscy sp. j"
  sheet["B5"] = "Ignatki 40/6"
  sheet["B6"] = "16-001 Kleosin"
  sheet["B7"] = "NIP 966 14 08 783"
  sheet["H3"] = "Dostawca"
  sheet["H4"] = "VITA POLYMERS POLAND SP. Z O.O."
  sheet["A8"] = "LP"
  sheet["I8"] = "UWAGI"

  rows = dataframe_to_rows(raport_vita)
  for r_idx, row in enumerate(rows, 1):
      for c_idx, value in enumerate(row, 1):
          sheet.cell(row=r_idx+7, column=c_idx, value=value)

  thin = Side(border_style="thin", color="000000")
  for row in sheet[f"A9:i{raport_vita.shape[0]+9}"]:
      for cell in row:
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

  wb.save(f"SPECYFIKACJA DO ZAMÓWIENIA DOS {' '.join(NR_zam.split('/'))}.xlsx")

def raport_vita(*args):
  """
  Zesatwaienie zamówionych pianek do VITA ilośiowe i z podziałem na bryły
  """
  
  pianki = [x.vita for x in args]
  zam_pianek_vita = pd.concat(pianki).fillna("")[["TYP", "NUMER", "ilosc", "PROFIL", "OZN", "OPIS", "WYMIAR"]]
  zam_pianek_vita.set_index(pd.Index([x for x in range(1,zam_pianek_vita.shape[0]+1)]),inplace=True)

  podsumowanie_zamowienia_vita = pd.concat(pianki).fillna("").sort_values(by="NUMER")
  podsumowanie_zamowienia_vita.set_index(pd.Index([x for x in range(1,podsumowanie_zamowienia_vita.shape[0]+1)]),inplace=True)

  return zam_pianek_vita, podsumowanie_zamowienia_vita[["TYP", "NUMER", "ilosc", "VOL", "PROFIL", "OZN", "OPIS", "WYMIAR"] + [x for x in podsumowanie_zamowienia_vita.columns if "br" in x]]


def raport_dostarczonych_pianek(cls, nr_dos="", drukuj_excel=False):
  """
  Zesatwianie ilosci pianek do modelu z dostawy
 
  cls -> zinicjalizowana instacja klasy zawierająca odpowiedni model

  nr_dos -> numer dostawy z saturn
  """
  zestawienie_pianek_do_bryly = list()

  for br in cls.bryly.keys():
    df = tab[(tab.MODEL == cls.MODEL) & (tab.BRYLA == br)]
    # df["ILOŚĆ"] = (df.ilosc * cls.bryly[br]).astype(int) #ilosc pianek * ilosc kompletów
    df["ILOŚĆ"] = (df.ilosc) #ilosc piabek w modelu wg dokumnetacja
    df["DOSTARCZONO/UWAGI"] = ""
    df = df[['TYP', 'PRZEZ', 'OR', 'OZN', 'PROFIL', 'NUMER', 'WYMIAR', 'ILOŚĆ', 'DOSTARCZONO/UWAGI']].fillna("-")
    df.set_index(pd.Index([x for x in range(1,df.shape[0]+1)]),inplace=True)
    zestawienie_pianek_do_bryly.append([br, df])

  def drukuj_zestawienie_dla_bryly_xlsx(zpdb_n):
    _df = zpdb_n[1]
    # _df = _df[_df.TYP != "G-401"]
    header = f"{cls.MODEL} {zpdb_n[0]} - {cls.bryly[zpdb_n[0]]:.0f}szt"
    print(header)
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.oddHeader.left.text = header
    sheet.oddHeader.left.size = 18
    sheet.oddHeader.left.font = "Calibry,Bold"
    sheet.oddHeader.right.text = f"Nr dostawy: {nr_dos}"
    sheet.append(["LP"]+list(_df.columns))
    rows = dataframe_to_rows(_df,header=False)
    for r in list(rows)[1:]:
      sheet.append(r)

    thin = Side(border_style="thin", color="000000")
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    for row in sheet[f"A1:J{_df.shape[0]+1}"]:
      for cell in row:
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

    path_ = f'Z:/160. ROZKRÓJ PIANEK/160.50 DOSTAWY PIANEK/{nr_dos.replace("/","_")}/'
    import os
    if not os.path.exists(path_):
      os.makedirs(path_)
    wb.save(path_ + f"{cls.MODEL[:3]} {zpdb_n[0]}.xlsx")
    # wb.save(f"{cls.MODEL[:3]} {zpdb_n[0]}.xlsx")

  if drukuj_excel:

    for i in zestawienie_pianek_do_bryly:
      drukuj_zestawienie_dla_bryly_xlsx(i)
    return 0

  return zestawienie_pianek_do_bryly