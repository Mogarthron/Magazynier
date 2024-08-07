from Modele_db import *
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, Boolean, Float
from datetime import datetime as dt
from sqlalchemy import select

# Base = declarative_base()

# class baza_PIANKI(Base):
#   __tablename__ = "baza_PAINKI"


# class WSPRZYMANE(Base):
#   __tablename__ = "WSTRZYMANE"

class RAPORT_KJ_DO_DOSTAWY_PIANEK(Base):
  __tablename__ = "RAPORT_KJ_DO_DOSTAWY_PIANEK"

  lp = Column("LP", Integer, primary_key=True, autoincrement=True)
  lp_zam_pianki = Column("LP_ZAM_PIANKI", Integer)
  nr_paczka = Column("NR_PACZKI", Integer)
  model = Column("MODEL", String)
  bryla_gen = Column("BRYLA_GEN", String)
  nr_pianki = Column("NR_PIANKI", String(6))
  blad_dopuszczalny_wysokosc = Column("BLAD_DOPUSZCZALNY_WYSOKOSC", Boolean, default=True)
  uwaga_wysokosc = Column("UWAGA_WYSOKOSC", String)
  blad_dopuszczalny_szerokosc = Column("BLAD_DOPUSZCZALNY_SZEROKOSC", Boolean, default=True)
  uwaga_szerokosc = Column("UWAGA_SZEROKOSC", String)
  blad_dopuszczalny_dlugosc = Column("BLAD_DOPUSZCZALNY_DLUGOSC", Boolean, default=True)
  uwaga_dlugosc = Column("UWAGA_DLUGOSC", String)
  blad_dopuszczalny = Column("BLAD_DOSPUSZCZALNY", Boolean, default=False)
  uwaga = Column("UWAGA", String, default="Brak uwag")
  data_dodania = Column("DATA_DODANIA", String(16), default=str(dt.now().strftime("%Y-%m-%d %H:%M")))
  
  def __init__(self, lp_zam_pianki, nr_paczka, model, bryla_gen, nr_pianki, blad_dopuszczalny_wysokosc, uwaga_wysokosc, 
               blad_dopuszczalny_szerokosc, uwaga_szerokosc, blad_dopuszczalny_dlugosc, uwaga_dlugosc, blad_dopuszczalny, uwaga):

    self.lp_zam_pianki = lp_zam_pianki
    self.nr_paczka = nr_paczka
    self.model = model
    self.bryla_gen = bryla_gen
    self.nr_pianki = nr_pianki
    self.blad_dopuszczalny_wysokosc = blad_dopuszczalny_wysokosc
    self.uwaga_wysokosc = uwaga_wysokosc
    self.blad_dopuszczalny_szerokosc = blad_dopuszczalny_szerokosc
    self.uwaga_szerokosc = uwaga_szerokosc
    self.blad_dopuszczalny_dlugosc = blad_dopuszczalny_dlugosc
    self.uwaga_dlugosc = uwaga_dlugosc
    self.blad_dopuszczalny = blad_dopuszczalny
    self.uwaga = uwaga

  
  def kj_to_json(self):
    return {
      "lp": self.lp,
      # "lpZamPianki": self.lp_zam_pianki,
      "dataDodania": self.data_dodania,
      "model": self.model,
      "brylaGen": self.bryla_gen,
      "nr_pianki": self.nr_pianki,
      "uwagaWysokosc": self.uwaga_wysokosc,
      "bDopWysokosc": self.blad_dopuszczalny_wysokosc,
      "uwagaSzerokosc": self.uwaga_szerokosc,
      "bDopSzerokosc": self.blad_dopuszczalny_szerokosc,
      "uwagaDlugosc": self.uwaga_dlugosc,
      "bDopDlugosc": self.blad_dopuszczalny_dlugosc,
      "dataDodania": self.data_dodania

  }

class KOMPLETY_PIANEK(Base):
  __tablename__ = "KOMPLETY_PIANEK"

  kod = Column("KOD", String(), primary_key=True)
  opis = Column("OPIS", String())
  stan_max = Column("MAX", Integer)
  czy_bryla = Column("CZY_BRYLA", Boolean, default=0)
  bryla_gen = Column("BRYLA_GEN", String())
  obj = Column("obj", Float)
  preferowany_czas_kj = Column("PREFEROWANY_CZAS_KJ", SmallInteger)
  preferowany_czas_pakowania = Column("PREFEROWANY_CZAS_PAKOWANIA", SmallInteger)
  magazyn_skladowania = Column("MAGAZYN_SKLADOWANIA", String(10))

class PRZYJECIE_ZEWNETRZE(Base):
  __tablename__ = "PRZYJECIE_ZEWNETRZNE"

  nr_pz = Column("NR_PZ", String(7),unique=True, primary_key=True)
  nr_zam = Column("NR_ZAM", String(7))
  data = Column("DATA", String(10))
  dostawca = Column("DOSTAWCA", String(50))
  nr_samochodu = Column("NR_SAMOCHODU", String(25))

  def __init__(self, nr_pz, nr_zam, data, dostawca, nr_samochodu):

    self.nr_pz = nr_pz
    self.nr_zam = nr_zam
    self.data = data
    self.dostawca = dostawca
    self.nr_samochodu = nr_samochodu

class PRZYJECIE_ZEWNETRZE_POZYCJE(Base):
  __tablename__ = "PRZYJECIE_ZEWNETRZNE_POZYCJE"

  lp = Column("LP", Integer, primary_key=True, autoincrement=True)
  nr_pz = Column("NR_PZ", String(7))
  kod = Column("KOD", String(20))
  opis = Column("OPIS", String)
  ilosc = Column("ILOSC", Integer)
  nr_kompletacji = Column("NR_KOMPLETACJI", String(5))
  uwagi_do_pozycji = Column("UWAGI_DO_POZYCJI", String)
  reklamacja = Column("REKLAMACJA", Boolean)

  def __init__(self, nr_pz, kod, opis, ilosc, nr_kompletacji):

    self.nr_pz = nr_pz
    self.kod = kod
    self.opis = opis
    self.ilosc = ilosc
    self.nr_kompletacji = nr_kompletacji

class AKTYWNE_DOSTAWY(Base):
  __tablename__ = "AKTYWNE_DOSTAWY"
  
  nr_zam = Column("NR_ZAM", String(7), unique=True, primary_key=True)
  dostawca = Column("DOSTAWCA", String(50))
  zamowienie_opis = Column("ZAMOWIENIE_OPIS", String)
  preferowana_data_dostawy = Column("PREFEROWANA_DATA_DOSTAWY", String(10))
  data_zamowienia = Column("DATA_ZAMOWIENIA", String(10))
  data_potwierdzenia_zamowienia = Column("DATA_POTWIERDZENIA_ZAMOWIENIA", String(10))
  uwagi = Column("UWAGI", String)
  polaczona_z_dos = Column("POLACZONA_Z_DOS", String(30))
  aktywna = Column("AKTYWNA", Integer)

  def __init__(self, nr_dos, dostawca, preferowana_data_dostawy, zamowienie_opis=""):
    
    self.nr_dos = nr_dos
    self.dostawca = dostawca
    self.zamowienie_opis = zamowienie_opis
    self.preferowana_data_dostawy = preferowana_data_dostawy
    self.data_zamowienia = None
    self.uwagi = None
    self.polaczona_z_dos = None
    self.aktywna = 0

  def __repr__(self):
      return f"{self.nr_zam}, {self.dostawca}, {self.data_zamowienia}, {self.preferowana_data_dostawy}, {self.aktywna}"

class BRAKI_PIANKI(Base):
  __tablename__ = "BRAKI_PIANKI"

  lpid = Column("LPID", Integer, autoincrement=True,  primary_key=True)
  lp = Column("LP", SmallInteger)
  pozycja = Column("POZYCJA", String)
  ilosc_brakow = Column("ILOSC_BRAKOW", SmallInteger)
  paczka = Column("PACZKA", String(5))
  data_kompletacji = Column("DATA_KOMPLETACJI", String(10))
  zamowione = Column("ZAMOWIONE", Integer)
  uwagi = Column("UWAGI", String)
  grupa = Column("GRUPA", Integer)
  tydzien_raportu = Column("TYDZIEN_RAPORTU", Integer)
  nr_zlecenia = Column("NR_ZLECENIA", String(10))
  naglowek_zlecenia = Column("NAGLOWEK_ZLECENIA", String)
  ilosc_na_zleceniu = Column("ILOSC_NA_ZLECENIU", Integer)
  opis_do_zlecenia = Column("OPIS_DO_ZLECENIA", String)
  data_wydania = Column("DATA_WYDANIA", String(10))
  data_zakonczenia = Column("DATA_ZAKONCZENIA", String(10))
  zamkniete = Column("ZAMKNIETE", Boolean)

class ZAM_PIANKI(Base):
  __tablename__ = "ZAM_PIANKI"

  lp = Column("LP", Integer, autoincrement=True,  primary_key=True)

  tydzien = Column("TYDZIEN", Integer)
  kod = Column("KOD", String)
  model = Column("MODEL", String)
  nr_kompletacji = Column("NR_KOMPLETACJI", String(5))
  opis = Column("OPIS", String)
  ile_zam = Column("ILE_ZAMOWIONE", Integer)
  znacznik_dostawcy = Column("ZNACZNIK_DOSTAWCY", String(2))
  galanteria = Column("GALANTERIA", String(1))
  siedziska_HR = Column("SIEDZISKA_HR", String(1))
  leniwa = Column("LENIWA", String(1))
  zam1 = Column("ZAM1", String(7))
  zam2 = Column("ZAM2", String(7))
  uwagi = Column("UWAGI", String)


  potw_dos1 = Column("POTW_DATA_DOS_1", String)
  potw_dos2 = Column("POTW_DATA_DOS_2", String)
  data_dos1 = Column("DATA_DOSTARCZENIA_1", String(10))
  data_dos2 = Column("DATA_DOSTARCZENIA_2", String(10))

  status_leniwa = Column("STATUS_LENIWA", String(50))
  status_leniwa_skoks = Column("STATUS_LENIWA_SKOSOWANIE", String(50))
  owaty_wydano = Column("OWATY_WYDANO", String(50))
  owaty_wycieto = Column("OWATY_WYCIETO", String(50))
  owaty_kompletacja = Column("OWATY_KOMPLETACJA", String(50))
  nr_pz = Column("nr_PZ", String)
  nr_pw = Column("nr_PW", String)
  status_kompletacja = Column("STATUS_KOMPLETACJA", String(50))
  nr_samochodu = Column("nr_SAMOCHODU", String(50))
  nr_partii = Column("nr_PARTII", String(5))

  def __init__(self, tydzien=None, model=None, kod=None, opis=None, ile_zam=None, znacznik_dostawcy=None, galanteria=None, siedziska_HR=None, leniwa=None, nr_kompletacji=None, zam1=None, zam2=None, uwagi=None, nr_partii=None):
    self.tydzien = tydzien
    self.kod = kod
    self.model = model
    self.nr_kompletacji = nr_kompletacji
    self.opis = opis
    self.ile_zam = ile_zam
    self.znacznik_dostawcy = znacznik_dostawcy
    self.galanteria = galanteria
    self.siedziska_HR = siedziska_HR
    self.leniwa = leniwa
    self.zam1 = zam1
    self.zam2 = zam2
    self.uwagi = uwagi
    self.nr_partii = nr_partii

  def plan_pracy_to_json(self):
    return {
            "lp": self.lp,
            "zam1": self.zam1 if type(self.zam1) == str else "",
            "zam2": self.zam2 if type(self.zam2) == str else "",
            "znacznikDostawcy": self.znacznik_dostawcy,
            "model": self.model,
            "nrKompletacji": self.nr_kompletacji,
            "opis": self.opis,
            "zamowione": int(self.ile_zam),
            "leniwa": self.status_leniwa if "AVANT" in self.opis else "ND",
            "leniwaSkos": self.status_leniwa_skoks if "AVANT" in self.opis else "ND",
            "owatyWydano": self.owaty_wydano,
            "owatyWycieto": self.owaty_wycieto,
            "owatyKompletacja": self.owaty_kompletacja,
            "statusKompletacja": self.status_kompletacja if type(self.status_kompletacja) == str else ""
        }
  
  def pianki_w_drodze_to_json(self):
    return {
            "lp": self.lp,
            "znacznikDostawcy": self.znacznik_dostawcy,
            "nrKompletacji": self.nr_kompletacji,
            "opis": self.opis,
            "zamowione": int(self.ile_zam),
            "zam1": self.zam1 if type(self.zam1) == str else "",
            "zam2": self.zam2 if type(self.zam2) == str else "",
            "gal": self.galanteria,
            "hrs": self.siedziska_HR,
            "mem": self.leniwa,
            "nrPartii": self.nr_partii,
            "nrSamochodu": self.nr_samochodu
        }


  def __repr__(self):
    return f"{self.tydzien}, {self.opis}"



class DOSTAWY(Base):
  __tablename__ = "DOSTAWY"

  lp = Column("LP", Integer, autoincrement=True,  primary_key=True)
  nr_samochodu = Column("NR_SAMOCHODU", String(20), nullable=False)
  nr_zam = Column("NR_ZAM", String(7))
  nr_partii = Column("nr_PARTII", String(5))
  obj_dostawy = Column("OBJ_DOSTAWY", SmallInteger, default=0)
  na_czas = Column("NA_CZAS", Boolean, default=None)
  zgodna_z_zam = Column("ZGODNA_Z_ZAM", Boolean, default=None)
  raport_bledow = Column("RAPORT_BLEDOW", String(8))

  def __init__(self, nr_samochodu, nr_zam, nr_partii):
    self.nr_samochodu = nr_samochodu
    self.nr_partii = nr_partii
    self.nr_zam = nr_zam

  def __repr__(self):
    return f"{self.lp}, {self.nr_samochodu}, {self.nr_zam}"
  

class DOSTAWY_POZYCJE(Base):
 __tablename__ = "DOSTAWY_POZYCJE"

 lp = Column("LP", Integer, autoincrement=True,  primary_key=True)
 nr_samochodu = Column("NR_SAMOCHODU", String(20))
 zam_pianki_id = Column("ZAM_PIANKI_ID", String(20))
 ile_kompletow = Column("ILE_KOMPLETOW", Integer)
 przyjechalo_kompletow = Column("PRZYJECHALO_KOMPLETOW", Integer)
 galanteria = Column("GALANTERIA", String(1))
 siedziska_HR = Column("SIEDZISKA_HR", String(1))
 leniwa = Column("LENIWA", String(1))
 uwagi_do_pozycji = Column("UWAGI_DO_POZYCJI", String(512))


