from Modele_db import *
from sqlalchemy import Column, String, Integer, Float, SmallInteger, Boolean, Date, DateTime
from datetime import datetime as dt


class STANY_MAGAZYNOWE_PIANEK(Base):
  __tablename__ = "STANY_MAGAZYNOWE_PIANEK"

  tydzien = Column(Integer, primary_key=True, autoincrement=False)
  ilosc_spakowana = Column(Integer)
  saldo = Column(Integer)
  wolne_saldo = Column(Integer)
  stan_max = Column(Integer)
  zamowienia_klientow = Column(Integer)
  prc_wolne_zam_max = Column(Float)
  
  def __init__(self, tydzien, ilosc_spakowana, saldo, wolne, stan_max, zamowienia_klientow, prc):
    self.tydzien = tydzien
    self.ilosc_spakowana = ilosc_spakowana
    self.saldo = saldo
    self.wolne_saldo = wolne
    self.stan_max = stan_max
    self.zamowienia_klientow = zamowienia_klientow
    self.prc_wolne_zam_max = prc


class SALDO(Base):
  __tablename__ = "SALDO"

  index = Column(Integer, primary_key=True, autoincrement=False)
  kod = Column(String(15))
  stan = Column(Integer)

class WSTRZYMANE(Base):
  __tablename__ = "WSTRZYMANE"

  index = Column(Integer, primary_key=True, autoincrement=False)
  kod = Column(String(15))
  ilosc = Column(Integer)

class NALICZONE(Base):
  __tablename__ = "NALICZONE"

  index = Column(Integer, primary_key=True, autoincrement=False)
  limit_nazwa = Column(String(12))
  kod = Column(String(15))
  zapot_zlec = Column(Integer)
  limit_data_prod = Column(DateTime)

class INSTRUKCJA_ZAMAWIANIA(Base):
  __tablename__ = "INSTRUKCJA_ZAMAWIANIA"
  
  izid = Column(Integer, primary_key=True)
  MODEL = Column(String(64)) 
  NAZWA_INSTRUKCJI = Column(String(64)) 
  DOSTAWCA_GAL =  Column(String(32))
  GALANTERIA = Column(String(128)) 
  DOSTAWCA_SHR =  Column(String(32))
  SIEDZISKA_HR = Column(String(128)) 
  DOSTAWCA_MEM =  Column(String(32))
  MEMORY = Column(String(128)) 
  OPIS = Column(String(128)) 
  AKTYWNA = Column(Boolean)

  def __init__(self, model, nazwa_instrukcji, dos_gal, gal, dos_shr, sied, dos_mem, memo, opis, aktywna=True):
    self.MODEL = model
    self.NAZWA_INSTRUKCJI = nazwa_instrukcji
    self.DOSTAWCA_GAL = dos_gal
    self.GALANTERIA = gal
    self.DOSTAWCA_SHR = dos_shr
    self.SIEDZISKA_HR = sied
    self.DOSTAWCA_MEM = dos_mem
    self.MEMORY = memo
    self.OPIS = opis
    self.AKTYWNA = aktywna

class PROPOZYCJA_ZAMOWIENIA(Base):
  __tablename__ = "PROPOZYCJA_ZAMOWIENIA"

  propozycja_zam_id = Column(Integer, primary_key=True)
  id_inst_zam = Column(Integer)
  bryla_id = Column(Integer)
  ilosc = Column(Integer)
  proponowana_ilosc = Column(Integer)
  nr_partii = Column(String(5))
  data_zamowienia = Column(DateTime)
  data_dostawy = Column(Date)
  dostawca = Column(String(32))
  nr_dos1 = Column(String(7))
  nr_dos2 = Column(String(7))

  akceptacja = Column(Boolean)
  data_akceptacji = Column(DateTime)
  uwagi = Column(String(256))

  def __init__(self, id_instrukcja_zamawiania, bryla_id, ilosc, proponowana_ilosc):
    self.id_inst_zam = id_instrukcja_zamawiania
    self.bryla_id = bryla_id
    self.ilosc = ilosc
    self.proponowana_ilosc = proponowana_ilosc
    self.data_zamowienia = dt.now()
    
  
class baza_STOLARNIA(Base):
  __tablename__ = "baza_STOLARNIA"

  bsid = Column(Integer, primary_key=True)
  MODEL = Column(String(64)) 
  BRYLA = Column(String(64)) 
  MATERIAL = Column(String(64))
  PRZEZ = Column(String(64)) 
  _CZAS = Column(String(64)) 
  _ILOSC = Column(String(64)) 
  OZNACZ = Column(String(64)) 
  NUMER = Column(String(64)) 
  WYMIAR = Column(String(16)) 
  WYS = Column(Integer) 
  SZER = Column(Integer) 
  DLUG = Column(Integer) 


class baza_PIANKI(Base):
  __tablename__ = "baza_PIANKI"

  index = Column(Integer, primary_key=True, autoincrement=False)
  MODEL = Column(String(64)) 
  BRYLA = Column(String(64)) 
  TYP = Column(String(64))
  PRZEZ = Column(String(64)) 
  OR = Column(String(64)) 
  OZN = Column(String(64)) 
  PROFIL = Column(String(64)) 
  NUMER = Column(String(64)) 
  ilosc = Column(Integer) 
  WYMIAR = Column(String(64)) 
  WYS = Column(Integer) 
  SZER = Column(Integer) 
  DLUG = Column(Integer) 
  GAL = Column(Float) 
  SHR = Column(Float) 
  MEM = Column(Float) 
  TOLERANCJA = Column(String(64))

class OWATY(Base):
    __tablename__ = "OWATY"

    oid = Column(Integer, primary_key=True)
    NAZWA_UKL = Column(String(64)) 
    OPIS = Column(String(64)) 
    RODZAJ_CIECIA = Column(String(64)) 
    ZUZYCIE = Column(Float) 
    TYP_OWATY = Column(String(64))



class TRANSPORTY(Base):
  __tablename__ = "TRANSPORTY"

  tlp = Column(Integer, primary_key=True, autoincrement=True)
  nr_transportu = Column(String(25), nullable=False)
  data_dostawy = Column(Date, nullable=False)  
  obietosc_planowana = Column(Float)
  obietosc_dostarczona = Column(Float)
  uwagi = Column(String(255), nullable=True)
  czas_rozladunku = Column(Integer)
  ppid = Column(Integer)
  nr_partii = Column(String(8))
  

  def __init__(self, nr_transportu, data_dostawy):
    self.nr_transportu = nr_transportu
    self.data_dostawy = data_dostawy

class TRANSPORTY_POZYCJE(Base):
  __tablename__ = "TRANSPORTY_POZYCJE"

  tplp = Column(Integer, primary_key=True, autoincrement=True)
  tlp = Column(Integer, nullable=False)
  zam_pianki_lp = Column(Integer, nullable=False)
  ile_przyjechalo = Column(Integer, nullable=False, default=0)
  przesuniete_na_transport = Column(String(25), nullable=True)
  uwagi = Column(String(255), nullable=True)
  data_dostawy = Column(Date, nullable=False)  

  def __init__(self, tlp, zam_pianki_lp):
    self.tlp = tlp
    self.zam_pianki_lp = zam_pianki_lp



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

  lp = Column(Integer, primary_key=True)
  kod = Column("KOD", String(15))
  opis = Column("OPIS", String(128))
  stan_max = Column("MAX", Integer)
  czy_bryla = Column("CZY_BRYLA", Boolean, default=0)
  bryla_gen = Column("BRYLA_GEN", String(32))
  obj = Column("obj", Float)
  preferowany_czas_kj = Column("PREFEROWANY_CZAS_KJ", SmallInteger)
  preferowany_czas_pakowania = Column("PREFEROWANY_CZAS_PAKOWANIA", SmallInteger)
  preferowany_czas_pakowania_memory = Column("PREFEROWANY_CZAS_PAKOWANIA_MEMORY", SmallInteger)
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
  lp = Column("LP", Integer)
  pozycja = Column("POZYCJA", String(128))
  ilosc_brakow = Column("ILOSC_BRAKOW", SmallInteger)
  paczka = Column("PACZKA", String(5))
  data_kompletacji = Column("DATA_KOMPLETACJI", String(10))
  zamowione = Column("ZAMOWIONE", Integer)
  uwagi = Column("UWAGI", String(128))
  grupa = Column("GRUPA", Integer)
  tydzien_raportu = Column("TYDZIEN_RAPORTU", Integer)
  nr_zlecenia = Column("NR_ZLECENIA", String(10))
  naglowek_zlecenia = Column("NAGLOWEK_ZLECENIA", String(128))
  ilosc_na_zleceniu = Column("ILOSC_NA_ZLECENIU", Integer)
  opis_do_zlecenia = Column("OPIS_DO_ZLECENIA", String(512))
  data_wydania = Column("DATA_WYDANIA", String(10))
  data_zakonczenia = Column("DATA_ZAKONCZENIA", String(10))
  zamkniete = Column("ZAMKNIETE", Boolean)


class ZAM_PIANKI(Base):
  __tablename__ = "ZAM_PIANKI"

  lp = Column("LP", Integer, autoincrement=True,  primary_key=True)

  tydzien = Column("TYDZIEN", Integer)
  kod = Column("KOD", String(16))
  model = Column("MODEL", String(128))
  nr_kompletacji = Column("NR_KOMPLETACJI", String(5))
  opis = Column("OPIS", String(128))
  ile_zam = Column("ILE_ZAMOWIONE", Integer)
  znacznik_dostawcy = Column("ZNACZNIK_DOSTAWCY", String(2))
  galanteria = Column("GALANTERIA", String(16))
  siedziska_HR = Column("SIEDZISKA_HR", String(16))
  leniwa = Column("LENIWA", String(16))
  zam1 = Column("ZAM1", String(7))
  zam2 = Column("ZAM2", String(7))
  uwagi = Column("UWAGI", String(512))

  potw_dos1 = Column("POTW_DATA_DOS_1", String)
  potw_dos2 = Column("POTW_DATA_DOS_2", String)
  data_dos1 = Column("DATA_DOSTARCZENIA_1", Date)
  data_dos2 = Column("DATA_DOSTARCZENIA_2", Date)

  status_leniwa = Column("STATUS_LENIWA", String(50))
  status_leniwa_skoks = Column("STATUS_LENIWA_SKOSOWANIE", String(50))
  owaty_wydano = Column("OWATY_WYDANO", Date)
  owaty_wycieto = Column("OWATY_WYCIETO", Date)
  owaty_kompletacja = Column("OWATY_KOMPLETACJA", Date)
  nr_pz = Column("nr_PZ", String)
  nr_pw = Column("nr_PW", String)
  status_kompletacja = Column("STATUS_KOMPLETACJA", String(50))
  data_zakonczenia = Column("DATA_ZAKONCZENIA", Date)
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
            "nr_partii": self.nr_partii,
            "zam1": self.zam1 if type(self.zam1) == str else "",
            "zam2": self.zam2 if type(self.zam2) == str else "",
            "znacznikDostawcy": self.znacznik_dostawcy,
            "model": self.model,
            "nrKompletacji": self.nr_kompletacji,
            "opis": self.opis,
            "zamowione": int(self.ile_zam),
            "leniwa": "BRAK KOLUMNY",#self.status_leniwa if "AVANT" in self.opis else "ND",
            "leniwaSkos": "BRAK KOLUMNY",#self.status_leniwa_skoks if "AVANT" in self.opis else "ND",
            "owatyWydano": "BRAK KOLUMNY",#self.owaty_wydano,
            "owatyWycieto": "BRAK KOLUMNY",#self.owaty_wycieto,
            "owatyKompletacja": "W TOKU" if self.owaty_kompletacja == None else self.owaty_kompletacja,
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



