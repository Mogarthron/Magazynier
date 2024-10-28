from Pianki.Analiza_pianek.funkcje_analizy_pianek import *
from Pianki.Modele_pianek.Pianki import Pianki

import plotly.graph_objects as go

class Analiza_Rodziny():
  def __init__(self, instrukcja_zamawiania:str, grupa_sprzedarzy=1, magazyn_skladowania=2, cls2=None):
    """
    instrukcja_zamawiania -> nazwa instrukcji zamawiania z bazy danych
    """

    kol_1 = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_1_MAX = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "MAX", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
    kol_2 = pda#"ZLECENIA"
    kol_3 = ["WST", "DO_ZAM_SZT"]
    kol_MAX = kol_1_MAX+kol_2+kol_3
    kol_skr = kol_1
    self.Instrukcja_zamawiania = instrukcja_zamawiania
    self.MODEL = "ELI_MIS" if instrukcja_zamawiania.split("_")[0] == "ELIMIS" else instrukcja_zamawiania.split("_")[0]
    # self.klasa = cls
    self.grupa_sprzedarzy = grupa_sprzedarzy
    self.magazyn_skladowania = magazyn_skladowania

    self.ana = analiza[analiza.OPIS.str.contains(self.MODEL)]

    self.ana["GRUPA_SPRZEDARZY"] = grupa_sprzedarzy

    self.ar = self.ana[kol_MAX[1:]]
    self.ar_skr = self.ana[kol_skr[1:]]
    self.bryly_do_zamowienia = self.ana[["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]
    self.analiza_obj = self.ana[[x for x in self.ana.columns if "obj" in x][1:]].sum()
    self.zamowienia = zam_pianki[zam_pianki.OPIS.str.contains(self.MODEL)]

    war_zagr = (self.ar.WOLNE_SALDO < self.ar.MIN) & (self.ar.WOLNE_SALDO >= 0)
    self.zagrozone = self.ar[war_zagr][["OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "MIN", "WOLNE_SALDO"]]

    self.krytyczne = self.ar[(self.ar.WOLNE_SALDO < 0)][["OPIS", "ZAMOWIONE","CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN"]+kol_2+["WST", "WOLNE_SALDO"]]

  def Bryly_do_zamowienia(self, wszystkie_bryly=False, zerowe_zam=False, lista_zagrozonych=False, lista_korekty_zam = False, korekta_zam:dict=None):
    """
    wszytkie_bryly -> zwraca tabele z wszystkimi bryłami w analize

    zerowe_zam -> ustawia kolumne z zerowymi ilościami zamówienia dal wszytkich brył w analizie

    lista_korekty_zam -> zwraca dict z bryłami ustawionymi do zamówienia
    
    karekta_zam -> dict z poporawionymi ilościami zamówień brył, funkcja zwróci DF z bryłami z analizy oraz podsymowanie pianek do VITA
    """

    if wszystkie_bryly:
      bdz = self.bryly_do_zamowienia
    else:
      if self.bryly_do_zamowienia.DO_ZAM_SZT.sum() == 0:
        bdz = self.bryly_do_zamowienia[["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]
      else:
        bdz = self.bryly_do_zamowienia[self.bryly_do_zamowienia.DO_ZAM_SZT > 0][["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]

    # print({i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()})

    if zerowe_zam:
      bdz["zero_zam"] = 0
      return bdz[["KOD", "OPIS", "BRYLA_GEN", "zero_zam"]]

    if lista_korekty_zam and type(lista_korekty_zam) != dict:
      return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()}
    
    if lista_korekty_zam and type(lista_korekty_zam) == dict:
      return lista_korekty_zam
    
    if lista_zagrozonych:
      li_zagr = self.zagrozone.merge(bdz.copy(), on="OPIS", how="left")[["BRYLA_GEN", "DO_ZAM_SZT"]]
      return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in li_zagr.iterrows()}

    if korekta_zam:
      kor = pd.DataFrame(korekta_zam.values(), columns=["KOREKTA_ZAM"], index=list(korekta_zam.keys())).reset_index().rename(columns={"index": "BRYLA_GEN"})
      kor_zam = bdz.merge(kor, how="right", on="BRYLA_GEN")[["KOD", "OPIS", "BRYLA_GEN", "KOREKTA_ZAM"]]
      bryly_kor_zam = {i[1].BRYLA_GEN: i[1].KOREKTA_ZAM for i in kor_zam[["BRYLA_GEN", "KOREKTA_ZAM"]].iterrows()}
      cls = Pianki(self.Instrukcja_zamawiania, bryly_kor_zam)
      # print(cls)
      return kor_zam[[ "KOD", "OPIS",  "KOREKTA_ZAM"]].rename(columns={"KOREKTA_ZAM": "DO_ZAMOWIENIA"}), cls

    return bdz, Pianki(self.Instrukcja_zamawiania, {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()})

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

  def Wykres_obj(self, nazwa_modelu=True, saldo=True, show_fig=True):
    # analiza_obj = analiza[analiza.RODZINA_NAZWA == self.MODEL[:3]][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]
    analiza_obj = analiza[analiza.OPIS.str.contains(self.MODEL)][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]

    bryly = analiza_obj["OPIS"].to_list()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.SALDO_obj.to_list() if saldo else analiza_obj.WOLNE_obj,
        name="SALDO_obj" if saldo else "WOLNE_obj",
        # offsetgroup=0
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.ZAMOWIONE_obj.to_list(),
        name="ZAMOWIONE_obj",
        # offsetgroup=0
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.CZEKA_NA_SPAKOWANIE_obj.to_list(),
        name="CZEKA_NA_SPAKOWANIE_obj",
        # offsetgroup=0
    ))
    fig.add_trace(go.Bar(
        x=bryly,
        y=analiza_obj.CZESCIOWO_DOSTARCZONE_obj.to_list(),
        name="CZESCIOWO_DOSTARCZONE_obj",
        # offsetgroup=0
    ))
    fig.add_trace(go.Bar(
        x=[f"{bryla}_MAX" for bryla in bryly],
        y=analiza_obj.MAX_obj.to_list(),
        name="MAX_obj",
        # offsetgroup=1,
        # offset=-0.5
    ))

    x_list = list()
    for x in bryly:
        x_list.append(x)
        x_list.append(f"{x}_MAX")



    if nazwa_modelu:
      fig.update_layout(
          title=f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX" if saldo else f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC WOLNA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3",
          barmode='stack',
          xaxis=dict(
              categoryorder="array",
              categoryarray=x_list  # Ręcznie ustawiona kolejność słupków na osi X
           ),
          bargap=0.15
          )
    else:
      fig.update_layout(
          title=f"OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX" if saldo else f"OBJETOSC ZAMOWIONA I OBJETOSC WOLNA DO OBJETOSCI MAX",
          xaxis_title="NAZAWA BRYLY",
          yaxis_title="OBIETOSC M3",
          barmode='stack',
          xaxis=dict(
              categoryorder="array",
              categoryarray=x_list  # Ręcznie ustawiona kolejność słupków na osi X
           ),
          bargap=0.15)

    if show_fig:
      fig.show()
    else:
      return fig

  def Zestawienie_na_rozkroj_pianek(self):
    
    return {
        "GRUPA":self.grupa_sprzedarzy,
        "MODEL": self.MODEL,
        "ZAMOWIONE_SIEDZISKA": self.analiza_obj.ZAMOWIONE_obj.sum(),
        "SALDO_STAN_OBECNY": self.analiza_obj.SALDO_obj.sum(),
        "SALDO_STAN_WOLNY": self.analiza_obj.WOLNE_obj.sum(),
        "SALDO_STAN_MAX": self.analiza_obj.MAX_obj.sum(),
        "WSPL_ZAP_SALDO": np.round(self.ana.SALDO_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
        "WSPL_ZAP_WOLNE": np.round(self.ana.WOLNE_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
        "WSPL_ZAP_ZAM": np.round((self.ana.WOLNE_obj.sum()+self.ana.ZAMOWIONE_obj.sum()+self.ana.CZEKA_NA_SPAKOWANIE_obj.sum()) / self.ana.MAX_obj.sum(), 2)*100
    }

  def Raport(self, prt=None):
    """
    prt = prtWs -> drukuje raport z wykresami obietosci salda

    prt = prtWw-> drukuje raport z wykresami obietosci wolnych

    prt = prt -> drukuje raport
    
    prt = None -> zwraca dict z raportem brakow
    """
    bdz = self.Bryly_do_zamowienia()[1]
    dzs = self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT

    if prt == "prtWs":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

      self.Wykres_obj(False)
      print("------------------------------------------------------------------")
      self.Wykres_podsumowanie_obj(False)
    
    elif prt == "prtWw":
      print(f"MODEL: {self.MODEL}")
      print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
      print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
      print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
      print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
      print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
      # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
      print("------------------------------------------------------------------")

      self.Wykres_obj(False,False)
      # print("------------------------------------------------------------------")
      # self.Wykres_podsumowanie_obj(False)

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
              "POZ_ZAGR": self.zagrozone.shape[0],
              "MIN": np.round(self.ana.MIN.sum(), 0),
              "MAX": np.round(self.ana.MAX.sum(), 0),
              "WOLNE": np.round(self.ana.WOLNE_SALDO.sum(), 0),
              "POZ_ZAGR_NIE_ZAM": self.zagrozone[(self.zagrozone.ZAMOWIONE+self.zagrozone.CZEKA_NA_SPAKOWANIE) == 0].shape[0],
              "BRAKI": self.krytyczne.shape[0],
              "ILOSC_BRAKOW": abs(self.krytyczne.WOLNE_SALDO.sum()),
              "BRYL_DO_ZAMOWIENIA": dzs.sum(),
              "WSPL_DO_ZAM": np.round(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj,2)*100,
              "OBJ_CIECH": np.round_(bdz.ciech_VOL,2),
              "OBJ_VITA": np.round_(bdz.vita_VOL,2),
              "OBJ_PIANPOL": np.round_(bdz.pianpol_VOL,2),
              "*WSPL_ZAP_WOLNE": np.round(self.ana.WOLNE_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
              "*WSPL_ZAP_ZAM": np.round((self.ana.WOLNE_obj.sum()+self.ana.ZAMOWIONE_obj.sum()+self.ana.CZEKA_NA_SPAKOWANIE_obj.sum()) / self.ana.MAX_obj.sum(), 2)*100,
              "MIN_obj": np.round(self.ana.MIN_obj.sum(), 0),
              "MAX_obj": np.round(self.ana.MAX_obj.sum(), 0),
              "SALDO_obj": np.round(self.ana.SALDO_obj.sum(), 0),
              "WOLNE_obj": np.round(self.ana.WOLNE_obj.sum(), 0),
              "ZAMOWIONE_NIE_PRZYJETE_obj": np.round(self.ana.ZAMOWIONE_NIE_PRZYJETE_obj.sum(), 0)
              }

  def __repr__(self):
      return f"MODEL: {self.MODEL}\n"+\
            f"BRYŁ DO ZAMÓWIENIA: {self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT.sum()}szt\n"+\
            f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%\n"
       







######################################################################
#STARA LOGIKA
######################################################################
# from Pianki.Analiza_pianek.funkcje_analizy_pianek import *

# import plotly.graph_objects as go

# class Analiza_Rodziny():
#   def __init__(self, cls, grupa_sprzedarzy=1, magazyn_skladowania=2, cls2=None):
#     """
#     cls -> KLASA MODELU PIANEK
#     """

#     kol_1 = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
#     kol_1_MAX = ["KOD", "OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN", "MAX", "SUMA_ZLEC", "WOLNE_SALDO", "WOLNE_NIE_SPAK"]
#     kol_2 = pda#"ZLECENIA"
#     kol_3 = ["WST", "DO_ZAM_SZT"]
#     kol_MAX = kol_1_MAX+kol_2+kol_3
#     kol_skr = kol_1
#     self.MODEL = cls.MODEL
#     self.klasa = cls
#     self.grupa_sprzedarzy = grupa_sprzedarzy
#     self.magazyn_skladowania = magazyn_skladowania

#     self.ana = analiza[analiza.OPIS.str.contains(cls.MODEL)]

#     self.ana["GRUPA_SPRZEDARZY"] = grupa_sprzedarzy

#     self.ar = self.ana[kol_MAX[1:]]
#     self.ar_skr = self.ana[kol_skr[1:]]
#     self.bryly_do_zamowienia = self.ana[["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]
#     self.analiza_obj = self.ana[[x for x in self.ana.columns if "obj" in x][1:]].sum()
#     self.zamowienia = zam_pianki[zam_pianki.OPIS.str.contains(self.MODEL)]

#     war_zagr = (self.ar.WOLNE_SALDO < self.ar.MIN) & (self.ar.WOLNE_SALDO >= 0)
#     self.zagrozone = self.ar[war_zagr][["OPIS", "ZAMOWIONE", "CZESIOWO_DOSTARCZONE", "CZEKA_NA_SPAKOWANIE", "SALDO", "MIN", "WOLNE_SALDO"]]

#     self.krytyczne = self.ar[(self.ar.WOLNE_SALDO < 0)][["OPIS", "ZAMOWIONE","CZEKA_NA_SPAKOWANIE", "SALDO", "SALDO_Z_NIE_SPAK", "MIN"]+kol_2+["WST", "WOLNE_SALDO"]]

#   def Bryly_do_zamowienia(self, wszystkie_bryly=False, zerowe_zam=False, lista_zagrozonych=False, lista_korekty_zam = False, korekta_zam:dict=None):
#     """
#     wszytkie_bryly -> zwraca tabele z wszystkimi bryłami w analize

#     zerowe_zam -> ustawia kolumne z zerowymi ilościami zamówienia dal wszytkich brył w analizie

#     lista_korekty_zam -> zwraca dict z bryłami ustawionymi do zamówienia
    
#     karekta_zam -> dict z poporawionymi ilościami zamówień brył, funkcja zwróci DF z bryłami z analizy oraz podsymowanie pianek do VITA
#     """

#     if wszystkie_bryly:
#       bdz = self.bryly_do_zamowienia
#     else:
#       bdz = self.bryly_do_zamowienia[self.bryly_do_zamowienia.DO_ZAM_SZT > 0][["KOD", "OPIS", "BRYLA_GEN", "DO_ZAM_SZT"]]

#     if zerowe_zam:
#       bdz["zero_zam"] = 0
#       return bdz[["KOD", "OPIS", "BRYLA_GEN", "zero_zam"]]

#     if lista_korekty_zam and type(lista_korekty_zam) != dict:
#       return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()}
    
#     if lista_korekty_zam and type(lista_korekty_zam) == dict:
#       return lista_korekty_zam
    
#     if lista_zagrozonych:
#       li_zagr = self.zagrozone.merge(bdz.copy(), on="OPIS", how="left")[["BRYLA_GEN", "DO_ZAM_SZT"]]
#       return {i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in li_zagr.iterrows()}

#     if korekta_zam:
#       kor = pd.DataFrame(korekta_zam.values(), columns=["KOREKTA_ZAM"], index=list(korekta_zam.keys())).reset_index().rename(columns={"index": "BRYLA_GEN"})
#       kor_zam = bdz.merge(kor, how="right", on="BRYLA_GEN")[["KOD", "OPIS", "BRYLA_GEN", "KOREKTA_ZAM"]]
#       bryly_kor_zam = {i[1].BRYLA_GEN: i[1].KOREKTA_ZAM for i in kor_zam[["BRYLA_GEN", "KOREKTA_ZAM"]].iterrows()}
#       cls = self.klasa(bryly_kor_zam)
#       # print(cls)
#       return kor_zam[[ "KOD", "OPIS",  "KOREKTA_ZAM"]].rename(columns={"KOREKTA_ZAM": "DO_ZAMOWIENIA"}), cls

#     return bdz, self.klasa({i[1].BRYLA_GEN: i[1].DO_ZAM_SZT for i in bdz[["BRYLA_GEN", "DO_ZAM_SZT"]].iterrows()})

#   def Wykres_podsumowanie_obj(self, nazwa_modelu=True):
#     dane_zam = self.analiza_obj
#     labels = dane_zam.index.to_list()
#     values = dane_zam.values

#     fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

#     if nazwa_modelu:
#       fig.update_layout(
#           title=f"{self.MODEL}: STOSUNKI OBIETOSCI",
#           )
#     else:
#       fig.update_layout(
#           title=f"STOSUNKI OBIETOSCI",
#           )

#     fig.show()

#   def Wykres_obj(self, nazwa_modelu=True, saldo=True, show_fig=True):
#     # analiza_obj = analiza[analiza.RODZINA_NAZWA == self.MODEL[:3]][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]
#     analiza_obj = analiza[analiza.OPIS.str.contains(self.MODEL)][["OPIS"]+[x for x in analiza.columns if "obj" in x][1:-1]]

#     bryly = analiza_obj["OPIS"].to_list()

#     fig = go.Figure()
#     fig.add_trace(go.Bar(
#         x=bryly,
#         y=analiza_obj.SALDO_obj.to_list() if saldo else analiza_obj.WOLNE_obj,
#         name="SALDO_obj" if saldo else "WOLNE_obj",
#         # offsetgroup=0
#     ))
#     fig.add_trace(go.Bar(
#         x=bryly,
#         y=analiza_obj.ZAMOWIONE_obj.to_list(),
#         name="ZAMOWIONE_obj",
#         # offsetgroup=0
#     ))
#     fig.add_trace(go.Bar(
#         x=bryly,
#         y=analiza_obj.CZEKA_NA_SPAKOWANIE_obj.to_list(),
#         name="CZEKA_NA_SPAKOWANIE_obj",
#         # offsetgroup=0
#     ))
#     fig.add_trace(go.Bar(
#         x=bryly,
#         y=analiza_obj.CZESCIOWO_DOSTARCZONE_obj.to_list(),
#         name="CZESCIOWO_DOSTARCZONE_obj",
#         # offsetgroup=0
#     ))
#     fig.add_trace(go.Bar(
#         x=[f"{bryla}_MAX" for bryla in bryly],
#         y=analiza_obj.MAX_obj.to_list(),
#         name="MAX_obj",
#         # offsetgroup=1,
#         # offset=-0.5
#     ))

#     x_list = list()
#     for x in bryly:
#         x_list.append(x)
#         x_list.append(f"{x}_MAX")



#     if nazwa_modelu:
#       fig.update_layout(
#           title=f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX" if saldo else f"{self.MODEL}: OBJETOSC ZAMOWIONA I OBJETOSC WOLNA DO OBJETOSCI MAX",
#           xaxis_title="NAZAWA BRYLY",
#           yaxis_title="OBIETOSC M3",
#           barmode='stack',
#           xaxis=dict(
#               categoryorder="array",
#               categoryarray=x_list  # Ręcznie ustawiona kolejność słupków na osi X
#            ),
#           bargap=0.15
#           )
#     else:
#       fig.update_layout(
#           title=f"OBJETOSC ZAMOWIONA I OBJETOSC SALDA DO OBJETOSCI MAX" if saldo else f"OBJETOSC ZAMOWIONA I OBJETOSC WOLNA DO OBJETOSCI MAX",
#           xaxis_title="NAZAWA BRYLY",
#           yaxis_title="OBIETOSC M3",
#           barmode='stack',
#           xaxis=dict(
#               categoryorder="array",
#               categoryarray=x_list  # Ręcznie ustawiona kolejność słupków na osi X
#            ),
#           bargap=0.15)

#     if show_fig:
#       fig.show()
#     else:
#       return fig

#   def Zestawienie_na_rozkroj_pianek(self):
    
#     return {
#         "GRUPA":self.grupa_sprzedarzy,
#         "MODEL": self.MODEL,
#         "ZAMOWIONE_SIEDZISKA": self.analiza_obj.ZAMOWIONE_obj.sum(),
#         "SALDO_STAN_OBECNY": self.analiza_obj.SALDO_obj.sum(),
#         "SALDO_STAN_WOLNY": self.analiza_obj.WOLNE_obj.sum(),
#         "SALDO_STAN_MAX": self.analiza_obj.MAX_obj.sum(),
#         "WSPL_ZAP_SALDO": np.round(self.ana.SALDO_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
#         "WSPL_ZAP_WOLNE": np.round(self.ana.WOLNE_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
#         "WSPL_ZAP_ZAM": np.round((self.ana.WOLNE_obj.sum()+self.ana.ZAMOWIONE_obj.sum()+self.ana.CZEKA_NA_SPAKOWANIE_obj.sum()) / self.ana.MAX_obj.sum(), 2)*100
#     }

#   def Raport(self, prt=None):
#     """
#     prt = prtWs -> drukuje raport z wykresami obietosci salda
#     prt = prtWw-> drukuje raport z wykresami obietosci wolnych
#     prt = prt -> drukuje raport
#     prt = None -> zwraca dict z raportem brakow
#     """
#     bdz = self.Bryly_do_zamowienia()[1]
#     dzs = self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT

#     if prt == "prtWs":
#       print(f"MODEL: {self.MODEL}")
#       print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
#       print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
#       print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
#       print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
#       print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
#       # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
#       print("------------------------------------------------------------------")

#       self.Wykres_obj(False)
#       print("------------------------------------------------------------------")
#       self.Wykres_podsumowanie_obj(False)
    
#     elif prt == "prtWw":
#       print(f"MODEL: {self.MODEL}")
#       print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
#       print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
#       print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
#       print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
#       print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
#       # print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
#       print("------------------------------------------------------------------")

#       self.Wykres_obj(False,False)
#       # print("------------------------------------------------------------------")
#       # self.Wykres_podsumowanie_obj(False)

#     elif prt == "prt":
#       print(f"MODEL: {self.MODEL}")
#       print(f"POZYCJE ZAGROZONE: {self.zagrozone.shape[0]} pozycji")
#       print(f"BRAKI: {self.krytyczne.shape[0]} pozycji")
#       print(f"ILOSC BRAKOW: {abs(self.krytyczne.WOLNE_SALDO.sum()):.0f} szt")
#       print(f"BRYŁ DO ZAMÓWIENIA: {dzs.sum()}szt")
#       print(f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%")
#       print(f"OBJ CIECH: {bdz.ciech_VOL:.0f}, OBJ VITA: {bdz.vita_VOL:.0f}, OBJ PIANPOL: {bdz.pianpol_VOL:.0f}")
#       print("------------------------------------------------------------------")

#     else:
#       return {"GRUPA":self.grupa_sprzedarzy,
#               "MODEL": self.MODEL,
#               "POZ_ZAGR": self.zagrozone.shape[0],
#               "MIN": np.round(self.ana.MIN.sum(), 0),
#               "MAX": np.round(self.ana.MAX.sum(), 0),
#               "WOLNE": np.round(self.ana.WOLNE_SALDO.sum(), 0),
#               "POZ_ZAGR_NIE_ZAM": self.zagrozone[(self.zagrozone.ZAMOWIONE+self.zagrozone.CZEKA_NA_SPAKOWANIE) == 0].shape[0],
#               "BRAKI": self.krytyczne.shape[0],
#               "ILOSC_BRAKOW": abs(self.krytyczne.WOLNE_SALDO.sum()),
#               "BRYL_DO_ZAMOWIENIA": dzs.sum(),
#               "WSPL_DO_ZAM": np.round(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj,2)*100,
#               "OBJ_CIECH": np.round_(bdz.ciech_VOL,2),
#               "OBJ_VITA": np.round_(bdz.vita_VOL,2),
#               "OBJ_PIANPOL": np.round_(bdz.pianpol_VOL,2),
#               "*WSPL_ZAP_WOLNE": np.round(self.ana.WOLNE_obj.sum() / self.ana.MAX_obj.sum(), 2)*100,
#               "*WSPL_ZAP_ZAM": np.round((self.ana.WOLNE_obj.sum()+self.ana.ZAMOWIONE_obj.sum()+self.ana.CZEKA_NA_SPAKOWANIE_obj.sum()) / self.ana.MAX_obj.sum(), 2)*100,
#               "MIN_obj": np.round(self.ana.MIN_obj.sum(), 0),
#               "MAX_obj": np.round(self.ana.MAX_obj.sum(), 0),
#               "SALDO_obj": np.round(self.ana.SALDO_obj.sum(), 0),
#               "WOLNE_obj": np.round(self.ana.WOLNE_obj.sum(), 0),
#               "ZAMOWIONE_NIE_PRZYJETE_obj": np.round(self.ana.ZAMOWIONE_NIE_PRZYJETE_obj.sum(), 0)
#               }

#   def __repr__(self):
#       return f"MODEL: {self.MODEL}\n"+\
#             f"BRYŁ DO ZAMÓWIENIA: {self.ana[self.ana.CZY_BRYLA == 1].DO_ZAM_SZT.sum()}szt\n"+\
#             f"OBJ BRYŁ DO ZAMÓWIENIA DO OBJETOSCI MAX: {(self.analiza_obj.DO_ZAM_obj / self.analiza_obj.MAX_obj)*100:.1f}%\n"
           