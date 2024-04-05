from Modele_db import *

Base = declarative_base()

class KOMPLETY_PIANEK(Base):
  __tablename__ = "KOMPLETY_PIANEK"

  kod = Column("KOD", String(), primary_key=True)
  opis = Column("OPIS", String())
  stan_max = Column("MAX", Integer)
  czy_bryla = Column("CZY_BRYLA", Boolean, default=0)
  bryla_gen = Column("BRYLA_GEN", String())

class PRZYJECIE_ZEWNETRZE(Base):
  __tablename__ = "PRZYJECIE_ZEWNETRZNE"

  nr_pz = Column("NR_PZ", String(7),unique=True, primary_key=True)
  nr_zam = Column("NR_ZAM", String(7))
  data = Column("DATA", String(10))
  dostawca = Column("DOSTAWCA", String(50))

  def __init__(self, nr_pz, nr_zam, data, dostawca):

    self.nr_pz = nr_pz
    self.nr_zam = nr_zam
    self.data = data
    self.dostawca = dostawca

class PRZYJECIE_ZEWNETRZE_POZYCJE(Base):
  __tablename__ = "PRZYJECIE_ZEWNETRZE_POZYCJE"

  lp = Column("LP", Integer, primary_key=True, autoincrement=True)
  nr_pz = Column("NR_PZ", String(7))
  kod = Column("KOD", String(20))
  opis = Column("OPIS", String())
  ilosc = Column("ILOSC", Integer)
  nr_kompletacji = Column("NR_KOMPLETACJI", String(5))

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
    self.aktywna = True

  def __repr__(self):
      return f"{self.nr_dos}, {self.dostawca}, {self.data_zamowienia}, {self.preferowana_data_dostawy}, {self.aktywna}"

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
  ile_zam = Column("ILE_ZAMOWIONE", Numeric)
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
  status_owaty = Column("STATUS_OWATY", String(50))
  nr_pz = Column("nr_PZ", String)
  nr_pw = Column("nr_PW", String)
  status_kompletacja = Column("STATUS_KOMPLETACJA", String(50))
  nr_samochodu = Column("nr_SAMOCHODU", String(50))

  def __init__(self, tydzien=None, model=None, kod=None, opis=None, ile_zam=None, znacznik_dostawcy=None, galanteria=None, siedziska_HR=None, leniwa=None, nr_kompletacji=None, zam1=None, zam2=None, uwagi=None):
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
            "owaty": self.status_owaty.split(",") if self.status_owaty else ["","",""],
            "statusKompletacja": self.status_kompletacja if type(self.status_kompletacja) == str else ""
        }


  def __repr__(self):
    return f"{self.tydzien}, {self.opis}"


class Lista_bryl_pianki(Base):
  __tablename__ = "lista_bryl_pianki"

  model = Column("Model", String(25), primary_key=True)
  lista_bryl = Column("lista_brył", String)

  def __init__(self, model, lista_bryl):
    self.model = model
    self.lista_bryl = lista_bryl

  def __repr__(self):
    return f"{self.model}, {len(self.lista_bryl.split('_'))}"





# Base.metadata.create_all(bind=engine)

# Session = sessionmaker(bind=engine)
# session = Session()

